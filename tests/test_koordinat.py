import math
import unittest

from gokbilim import koordinat as k


def _h(saat, dakika, saniye):
    return 15.0 * (saat + dakika / 60.0 + saniye / 3600.0)


def _d(derece, dakika, saniye):
    return derece + dakika / 60.0 + saniye / 3600.0


class BicimTests(unittest.TestCase):
    def test_ra_meeus_12a(self):
        # Meeus 12.a: 13h10m46.3668s = 197.693195°; 0.001 s'ye yuvarlanır.
        self.assertEqual(k.ra_hms(197.693195), (13, 10, 46.367))
        self.assertEqual(k.ra_metni(197.693195), "13:10:46.367")

    def test_ra_sinirlari(self):
        self.assertEqual(k.ra_hms(0), (0, 0, 0.0))
        self.assertEqual(k.ra_hms(180), (12, 0, 0.0))
        # Yuvarlama 24h'ye taşarsa 0h'a sarılır.
        self.assertEqual(k.ra_hms(359.9999999), (0, 0, 0.0))

    def test_dec_isaret_korunur(self):
        self.assertEqual(k.dec_dms(-0.5), ("-", 0, 30, 0.0))
        self.assertEqual(k.dec_metni(-0.5), "-00:30:00.000")
        self.assertEqual(k.dec_metni(0), "+00:00:00.000")
        self.assertEqual(k.dec_dms(45.504167), ("+", 45, 30, 15.001))
        self.assertEqual(k.dec_dms(-90), ("-", 90, 0, 0.0))

    def test_gecersiz_aralik(self):
        for kotu in (-1, 360, float("nan"), float("inf"), True, "10"):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                k.ra_hms(kotu)
        for kotu in (-90.1, 90.1, float("nan"), None):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                k.dec_dms(kotu)


class AyristirmaTests(unittest.TestCase):
    def test_ra_bicimleri_ayni_degeri_verir(self):
        beklenen = _h(12, 30, 45)
        for metin in ("12h30m45s", "12:30:45", "12 30 45", "12H30M45S"):
            with self.subTest(metin=metin):
                self.assertAlmostEqual(k.ra_ayristir(metin), beklenen, places=9)
        self.assertAlmostEqual(k.ra_ayristir("12h30m"), 187.5, places=9)
        self.assertAlmostEqual(k.ra_ayristir("12h"), 180.0, places=9)
        self.assertAlmostEqual(k.ra_ayristir("12:30:45.5"), _h(12, 30, 45.5), places=9)

    def test_ra_derece(self):
        self.assertEqual(k.ra_ayristir("187.5"), 187.5)
        self.assertEqual(k.ra_ayristir("187.5°"), 187.5)
        self.assertEqual(k.ra_ayristir("187.5d"), 187.5)

    def test_dec_bicimleri(self):
        beklenen = _d(45, 30, 15)
        for metin in ("+45:30:15", "45:30:15", "45d30m15s", "+45°30′15″", "+45 30 15"):
            with self.subTest(metin=metin):
                self.assertAlmostEqual(k.dec_ayristir(metin), beklenen, places=9)
        self.assertEqual(k.dec_ayristir("-12.5"), -12.5)

    def test_dec_eksi_sifir_derece(self):
        # İşaret ayrı okunmazsa -00:30:00 yanlışlıkla +0.5° olurdu.
        self.assertAlmostEqual(k.dec_ayristir("-00:30:00"), -0.5, places=12)
        self.assertAlmostEqual(k.dec_ayristir("−00:30:00"), -0.5, places=12)

    def test_gidis_donus(self):
        for ra, dec in ((0.0, 0.0), (197.693195, -26.431), (359.5, 89.9999), (12.3456, -89.5)):
            with self.subTest(ra=ra, dec=dec):
                self.assertAlmostEqual(k.ra_ayristir(k.ra_metni(ra)), ra, delta=0.0003)
                self.assertAlmostEqual(k.dec_ayristir(k.dec_metni(dec)), dec, delta=0.0003)

    def test_gecersiz_metinler(self):
        for kotu in ("", "abc", "25h", "12h60m", "12h30.5m10s", "12h30m45s extra", "-5", "360", "1 2 3 4", None, 12):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                k.ra_ayristir(kotu)
        for kotu in ("", "91:00:00", "-90:00:01", "45:60:00", "45d30.5m10s", "x", None, 45):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                k.dec_ayristir(kotu)


class AciUzakligiTests(unittest.TestCase):
    ARCTURUS = (_h(14, 15, 39.7), _d(19, 10, 57))
    SPICA = (_h(13, 25, 11.6), -_d(11, 9, 41))

    def test_meeus_17a(self):
        for islev in (k.aci_uzakligi, k.aci_uzakligi_vektor):
            with self.subTest(islev=islev.__name__):
                self.assertAlmostEqual(islev(*self.ARCTURUS, *self.SPICA), 32.7930, places=4)

    def test_geometrik_durumlar(self):
        # Ekvator üzerinde RA farkı doğrudan açıdır; kutuplar 180° ayrıdır.
        for islev in (k.aci_uzakligi, k.aci_uzakligi_vektor):
            with self.subTest(islev=islev.__name__):
                self.assertAlmostEqual(islev(10, 0, 20, 0), 10.0, places=9)
                self.assertAlmostEqual(islev(0, 0, 90, 0), 90.0, places=9)
                self.assertAlmostEqual(islev(0, 0, 0, 1), 1.0, places=9)
                self.assertAlmostEqual(islev(123, 45, 123, 45), 0.0, places=9)
                self.assertAlmostEqual(islev(0, 90, 77, -90), 180.0, places=9)
                self.assertAlmostEqual(islev(0, 0, 180, 0), 180.0, places=9)

    def test_bir_yay_saniyesi(self):
        saniye = 1.0 / 3600.0
        self.assertAlmostEqual(k.aci_uzakligi(50, 30, 50, 30 + saniye), saniye, places=12)
        self.assertAlmostEqual(k.aci_uzakligi_vektor(50, 30, 50, 30 + saniye), saniye, places=12)

    def test_iki_surum_tutarli(self):
        noktalar = ((1.0, 2.0, 3.0, 4.0), (359.9, -45.0, 0.1, 45.0), (200.0, 85.0, 20.0, 86.0))
        for nokta in noktalar:
            self.assertAlmostEqual(k.aci_uzakligi(*nokta), k.aci_uzakligi_vektor(*nokta), places=9)

    def test_gecersiz(self):
        with self.assertRaises(ValueError):
            k.aci_uzakligi(361, 0, 0, 0)
        with self.assertRaises(ValueError):
            k.aci_uzakligi_vektor(0, 91, 0, 0)


class GalaktikTests(unittest.TestCase):
    # Bağımsız ikinci gösterim: Kuzey Galaktik Kutup (J2000) ve l(KGK) açıları.
    A_G, D_G, L_KGK = 192.85948, 27.12825, 122.93192

    def _acilarla(self, ra, dec):
        a, d, ag, dg = (math.radians(v) for v in (ra, dec, self.A_G, self.D_G))
        sin_b = math.sin(d) * math.sin(dg) + math.cos(d) * math.cos(dg) * math.cos(a - ag)
        y = math.cos(d) * math.sin(a - ag)
        x = math.sin(d) * math.cos(dg) - math.cos(d) * math.sin(dg) * math.cos(a - ag)
        return (self.L_KGK - math.degrees(math.atan2(y, x))) % 360.0, math.degrees(math.asin(sin_b))

    def test_galaktik_merkez(self):
        # IAU tanımı: l = 0, b = 0 noktası 17h45m37.224s, −28°56′10.23″ (J2000).
        l, b = k.ekvatordan_galaktige(_h(17, 45, 37.224), -_d(28, 56, 10.23))
        self.assertLess(min(l, 360.0 - l), 1e-3)
        self.assertLess(abs(b), 1e-3)

    def test_kuzey_galaktik_kutup(self):
        l, b = k.ekvatordan_galaktige(self.A_G, self.D_G)
        self.assertAlmostEqual(b, 90.0, delta=1e-3)

    def test_vega(self):
        # Vega (J2000: 18h36m56.336s, +38°47′01.28″): l ≈ 67.45°, b ≈ +19.24°.
        l, b = k.ekvatordan_galaktige(_h(18, 36, 56.336), _d(38, 47, 1.28))
        self.assertAlmostEqual(l, 67.45, delta=0.01)
        self.assertAlmostEqual(b, 19.24, delta=0.01)

    def test_matris_aci_formuluyla_uyumlu(self):
        for ra, dec in ((0.0, 0.0), (83.633, 22.0145), (266.4, -28.9), (150.0, 60.0), (300.0, -75.0), (10.0, 89.0)):
            with self.subTest(ra=ra, dec=dec):
                l, b = k.ekvatordan_galaktige(ra, dec)
                l2, b2 = self._acilarla(ra, dec)
                self.assertAlmostEqual(b, b2, delta=1e-3)
                self.assertLess(min(abs(l - l2), 360.0 - abs(l - l2)), 1e-3)

    def test_gidis_donus(self):
        for ra, dec in ((0.0, 0.0), (83.633, 22.0145), (266.4, -28.9), (359.9, -89.0), (180.0, 90.0)):
            with self.subTest(ra=ra, dec=dec):
                ra2, dec2 = k.galaktikten_ekvatora(*k.ekvatordan_galaktige(ra, dec))
                self.assertAlmostEqual(dec2, dec, places=7)
                if abs(dec) < 89.999:
                    self.assertLess(min(abs(ra2 - ra), 360.0 - abs(ra2 - ra)), 1e-6)

    def test_gecersiz_galaktik(self):
        for l, b in ((360, 0), (-1, 0), (0, 91), (float("nan"), 0), (True, 0)):
            with self.subTest(l=l, b=b), self.assertRaises(ValueError):
                k.galaktikten_ekvatora(l, b)


if __name__ == "__main__":
    unittest.main()
