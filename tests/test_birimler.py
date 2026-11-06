import math
import unittest

from gokbilim import birimler as b


class DonusumTests(unittest.TestCase):
    def test_tanim_geregi_degerler(self):
        # 1 pc = 648000/π AU; 1 ly = c × Jülyen yılı; 1 AU = 149597870700 m (tam).
        self.assertEqual(b.uzunluk_cevir(1, "au", "m"), 149597870700.0)
        self.assertAlmostEqual(b.uzunluk_cevir(1, "pc", "m"), 3.0856775814913673e16, delta=1e2)
        self.assertEqual(b.uzunluk_cevir(1, "ly", "m"), 9460730472580800.0)

    def test_parsek_isik_yili(self):
        self.assertAlmostEqual(b.uzunluk_cevir(1, "pc", "ly"), 3.2615637771674, places=9)
        self.assertAlmostEqual(b.uzunluk_cevir(1, "pc", "au"), 206264.806247, places=5)

    def test_gunes_dunya_ortalamasi(self):
        # Güneş-Dünya ışık süresi ≈ 499 s (8 dk 19 s).
        self.assertAlmostEqual(b.uzunluk_cevir(1, "au", "m") / b.ISIK_HIZI, 499.0, delta=0.01)
        self.assertAlmostEqual(b.uzunluk_cevir(1, "au", "r_gunes"), 215.03, delta=0.01)

    def test_kutle(self):
        self.assertAlmostEqual(b.kutle_cevir(1, "m_gunes", "kg"), 1.98841e30, delta=1e26)
        self.assertAlmostEqual(b.kutle_cevir(1, "m_gunes", "m_dunya"), 332946.0, delta=5)
        # Güneş/Jüpiter kütle oranı: IAU 2015 nominal GM_J ile 1047.57, uyduları dahil Jüpiter sistemi
        # ile 1047.35 (farklı sabitler); ikisini de kapsayan bir aralık beklenir.
        self.assertAlmostEqual(b.kutle_cevir(1, "m_gunes", "m_jupiter"), 1047.45, delta=0.3)

    def test_zaman_ve_aci(self):
        self.assertEqual(b.zaman_cevir(1, "yil", "gun"), 365.25)
        self.assertEqual(b.zaman_cevir(2, "saat", "dk"), 120.0)
        self.assertAlmostEqual(b.aci_cevir(1, "derece", "yay_saniyesi"), 3600.0, places=9)
        self.assertAlmostEqual(b.aci_cevir(math.pi, "radyan", "derece"), 180.0, places=9)
        self.assertAlmostEqual(b.aci_cevir(1, "yay_saniyesi", "mas"), 1000.0, places=9)

    def test_gidis_donus(self):
        for deger in (1e-5, 1.0, 123.456, 1e9):
            self.assertAlmostEqual(b.uzunluk_cevir(b.uzunluk_cevir(deger, "pc", "ly"), "ly", "pc"), deger,
                                   delta=deger * 1e-12)

    def test_gecersiz(self):
        for deger in (float("nan"), float("inf"), True, "1", None):
            with self.subTest(deger=deger), self.assertRaises(ValueError):
                b.uzunluk_cevir(deger, "m", "km")
        with self.assertRaises(ValueError):
            b.uzunluk_cevir(1, "mil", "km")
        with self.assertRaises(ValueError):
            b.kutle_cevir(1, "kg", "pound")


if __name__ == "__main__":
    unittest.main()
