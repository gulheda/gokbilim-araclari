import unittest
from datetime import date, datetime, timedelta, timezone

from gokbilim import gozlem as g


def _utc(ay, gun, saat, dakika, yil=2026):
    return datetime(yil, ay, gun, saat, dakika, tzinfo=timezone.utc)


class GunesKonumuTests(unittest.TestCase):
    def test_meeus_25a(self):
        # Meeus örnek 25.a: 1992-10-13 0h (JD 2448908.5).
        ra, dec, r = g.gunes_konumu(datetime(1992, 10, 13, tzinfo=timezone.utc))
        self.assertAlmostEqual(ra, 198.38083, delta=0.0005)
        self.assertAlmostEqual(dec, -7.78507, delta=0.0005)
        self.assertAlmostEqual(r, 0.99766, delta=0.00002)

    def test_gunes_gecisleri(self):
        # Gündönümü civarında Dec ≈ ±23.44°; ekinokslarda ≈ 0°; uzaklık yıl boyunca 0.983-1.017 AU.
        self.assertAlmostEqual(g.gunes_konumu(_utc(6, 21, 12, 0))[1], 23.44, delta=0.02)
        self.assertAlmostEqual(g.gunes_konumu(_utc(12, 21, 12, 0))[1], -23.44, delta=0.02)
        self.assertAlmostEqual(g.gunes_konumu(_utc(3, 20, 14, 46))[1], 0.0, delta=0.05)
        for ay in range(1, 13):
            self.assertTrue(0.983 <= g.gunes_konumu(_utc(ay, 1, 0, 0))[2] <= 1.017)

    def test_saat_dilimsiz_reddedilir(self):
        with self.assertRaises(ValueError):
            g.gunes_konumu(datetime(2026, 1, 1))


class GunesOlaylariTests(unittest.TestCase):
    """Beklenen değerler: ABD Deniz Gözlemevi (USNO) Rise/Set API'si, UTC, dakika hassasiyeti.

    Kaynak: https://aa.usno.navy.mil/api/rstt/oneday (2026-11-07 tarihinde alındı).
    """
    DAKIKA = timedelta(minutes=2)

    VAKALAR = {
        # ad: (gün, enlem, boylam, (doğuş, tepe, batış), (sivil başı, sivil sonu))
        "Istanbul 7 Kasım": (date(2026, 11, 7), 41.01, 28.98,
                             (_utc(11, 7, 4, 42), _utc(11, 7, 9, 48), _utc(11, 7, 14, 53)),
                             (_utc(11, 7, 4, 13), _utc(11, 7, 15, 22))),
        "Istanbul 21 Haziran": (date(2026, 6, 21), 41.01, 28.98,
                                (_utc(6, 21, 2, 32), _utc(6, 21, 10, 6), _utc(6, 21, 17, 40)),
                                (_utc(6, 21, 1, 58), _utc(6, 21, 18, 13))),
        "Ankara 20 Mart": (date(2026, 3, 20), 39.93, 32.86,
                           (_utc(3, 20, 3, 52), _utc(3, 20, 9, 56), _utc(3, 20, 16, 0)),
                           (_utc(3, 20, 3, 25), _utc(3, 20, 16, 27))),
        # Doğuş bir önceki UTC gününe düşer (tepe 21 Aralık 01:53 UTC); USNO'nun 20 Aralık kaydı.
        "Sydney 21 Aralık": (date(2026, 12, 21), -33.87, 151.21,
                             (_utc(12, 20, 18, 41), _utc(12, 21, 1, 53), _utc(12, 21, 9, 5)),
                             (_utc(12, 20, 18, 11), _utc(12, 21, 9, 34))),
    }

    def test_usno_ile_uyum(self):
        for ad, (gun, enlem, boylam, ana, sivil) in self.VAKALAR.items():
            with self.subTest(ad=ad):
                bulunan = g.gunes_olaylari(gun, enlem, boylam)
                for beklenen, gercek in zip(ana, bulunan):
                    self.assertLessEqual(abs(gercek - beklenen), self.DAKIKA, (ad, beklenen, gercek))
                sb, _, ss = g.gunes_olaylari(gun, enlem, boylam, g.SIVIL_ALACAKARANLIK)
                self.assertLessEqual(abs(sb - sivil[0]), self.DAKIKA, (ad, "sivil baş"))
                self.assertLessEqual(abs(ss - sivil[1]), self.DAKIKA, (ad, "sivil son"))

    def test_olayda_yukseklik_hedefe_esit(self):
        # Kendi içinde tutarlılık: bulunan anda Güneş merkezi hedef yükseklikte olmalı.
        for ad, (gun, enlem, boylam, _, _) in self.VAKALAR.items():
            for hedef in (g.GUNES_UFKU, g.SIVIL_ALACAKARANLIK, g.ASTRONOMIK_ALACAKARANLIK):
                yuk, tepe, bat = g.gunes_olaylari(gun, enlem, boylam, hedef)
                for an in (yuk, bat):
                    if an is not None:
                        with self.subTest(ad=ad, hedef=hedef):
                            self.assertAlmostEqual(g.gunes_yuksekligi(an, enlem, boylam), hedef, delta=0.02)

    def test_sira_dogru(self):
        for ad, (gun, enlem, boylam, _, _) in self.VAKALAR.items():
            yuk, tepe, bat = g.gunes_olaylari(gun, enlem, boylam)
            with self.subTest(ad=ad):
                self.assertLess(yuk, tepe)
                self.assertLess(tepe, bat)
                self.assertGreater(g.gunes_yuksekligi(tepe, enlem, boylam), 0)

    def test_kutup_gecesi_ve_gece_yarisi_gunesi(self):
        # Tromsø (69.65 K): Aralıkta Güneş doğmaz, Haziranda batmaz; tepe noktası yine de vardır.
        kis = g.gunes_olaylari(date(2026, 12, 21), 69.65, 18.96)
        self.assertEqual((kis[0], kis[2]), (None, None))
        self.assertLess(g.gunes_yuksekligi(kis[1], 69.65, 18.96), g.GUNES_UFKU)
        yaz = g.gunes_olaylari(date(2026, 6, 21), 69.65, 18.96)
        self.assertEqual((yaz[0], yaz[2]), (None, None))
        self.assertGreater(g.gunes_yuksekligi(yaz[1], 69.65, 18.96), 40)

    def test_datetime_girdisi(self):
        a = g.gunes_olaylari(date(2026, 11, 7), 41.01, 28.98)
        b = g.gunes_olaylari(_utc(11, 7, 23, 30), 41.01, 28.98)
        self.assertEqual(a, b)

    def test_gecersiz(self):
        gun = date(2026, 11, 7)
        for enlem, boylam, yukseklik in ((91, 0, -0.8), (0, 181, -0.8), (0, float("nan"), -0.8),
                                         (0, 0, 91), (0, 0, float("nan")), (0, True, -0.8), (float("nan"), 0, -0.8)):
            with self.subTest(enlem=enlem, boylam=boylam, yukseklik=yukseklik), self.assertRaises(ValueError):
                g.gunes_olaylari(gun, enlem, boylam, yukseklik)


class YuksekDegerCizelgesiTests(unittest.TestCase):
    ENLEM, BOYLAM = 41.01, 28.98

    def test_sayi_ve_uclar(self):
        bas, bit = _utc(11, 7, 0, 0), _utc(11, 7, 6, 0)
        satirlar = g.yukseklik_cizelgesi(150.0, 20.0, bas, bit, 30, self.ENLEM, self.BOYLAM)
        self.assertEqual(len(satirlar), 13)
        self.assertEqual((satirlar[0][0], satirlar[-1][0]), (bas, bit))
        self.assertEqual([satir[0] for satir in satirlar], sorted(satir[0] for satir in satirlar))

    def test_degerler_tek_tek_ayni(self):
        from gokbilim import koordinat
        an = _utc(11, 7, 3, 0)
        (bulunan,) = g.yukseklik_cizelgesi(150.0, 20.0, an, an, 60, self.ENLEM, self.BOYLAM)
        self.assertEqual(bulunan[1:], koordinat.ekvatordan_ufka(150.0, 20.0, an, self.ENLEM, self.BOYLAM))

    def test_gunes_tepede_en_yuksek(self):
        # Güneş'in RA/Dec'iyle: çizelgedeki en yüksek an, hesaplanan tepe anına 10 dk içinde yakın olmalı.
        gun = date(2026, 6, 21)
        _, tepe, _ = g.gunes_olaylari(gun, self.ENLEM, self.BOYLAM)
        ra, dec, _ = g.gunes_konumu(tepe)
        satirlar = g.yukseklik_cizelgesi(ra, dec, tepe - timedelta(hours=3), tepe + timedelta(hours=3),
                                         5, self.ENLEM, self.BOYLAM)
        en_yuksek = max(satirlar, key=lambda s: s[2])
        self.assertLessEqual(abs(en_yuksek[0] - tepe), timedelta(minutes=10))
        self.assertAlmostEqual(en_yuksek[2], 90.0 - self.ENLEM + dec, delta=0.1)

    def test_gecersiz(self):
        bas, bit = _utc(11, 7, 0, 0), _utc(11, 7, 6, 0)
        for adim in (0, 1441, float("nan"), True, "30"):
            with self.subTest(adim=adim), self.assertRaises(ValueError):
                g.yukseklik_cizelgesi(0, 0, bas, bit, adim, self.ENLEM, self.BOYLAM)
        with self.assertRaises(ValueError):
            g.yukseklik_cizelgesi(0, 0, bit, bas, 30, self.ENLEM, self.BOYLAM)
        with self.assertRaises(ValueError):
            g.yukseklik_cizelgesi(0, 0, datetime(2026, 1, 1), bit, 30, self.ENLEM, self.BOYLAM)
        with self.assertRaises(ValueError):
            g.yukseklik_cizelgesi(0, 0, _utc(1, 1, 0, 0), _utc(12, 31, 0, 0, yil=2030), 1, self.ENLEM, self.BOYLAM)


if __name__ == "__main__":
    unittest.main()
