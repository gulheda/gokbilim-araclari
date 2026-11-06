import math
import unittest

from gokbilim import fotometri as f


class BuyuklukAkiTests(unittest.TestCase):
    def test_pogson(self):
        # 5 büyüklük farkı tam 100 kat; 1 büyüklük ≈ 2.512 kat.
        self.assertAlmostEqual(f.aki_orani(0, 5), 100.0, places=9)
        self.assertAlmostEqual(f.aki_orani(5, 0), 0.01, places=12)
        self.assertAlmostEqual(f.aki_orani(0, 1), 2.512, places=3)
        self.assertEqual(f.aki_orani(7.3, 7.3), 1.0)

    def test_buyukluk_farki(self):
        self.assertAlmostEqual(f.buyukluk_farki(1, 100), 5.0, places=9)
        self.assertAlmostEqual(f.buyukluk_farki(100, 1), -5.0, places=9)
        self.assertAlmostEqual(f.buyukluk_farki(f.aki_orani(3.2, 8.9), 1), 3.2 - 8.9, places=9)

    def test_hata_yayilimi(self):
        # %10 akı hatası ≈ 0.1086 büyüklük (2.5 / ln 10 = 1.0857).
        self.assertAlmostEqual(f.buyukluk_hatasi(100, 10), 0.10857, places=5)
        self.assertEqual(f.buyukluk_hatasi(50, 0), 0.0)

    def test_gecersiz(self):
        for kotu in (float("nan"), float("inf"), True, "1", None):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.aki_orani(kotu, 1)
        for kotu in (0, -1.0):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.buyukluk_farki(kotu, 1)
        with self.assertRaises(ValueError):
            f.buyukluk_hatasi(10, -1)


class UzaklikModuluTests(unittest.TestCase):
    def test_on_parsek_ve_yuz_parsek(self):
        self.assertAlmostEqual(f.uzaklik_modulu(10), 0.0, places=12)
        self.assertAlmostEqual(f.uzaklik_modulu(100), 5.0, places=12)
        self.assertAlmostEqual(f.uzaklik_modulu(1000), 10.0, places=12)
        self.assertEqual(f.mutlak_buyukluk(4.0, 10), 4.0)

    def test_gunes(self):
        # Güneş (V): m = -26.74, d = 1 AU = 4.8481e-6 pc  =>  M ≈ 4.83.
        self.assertAlmostEqual(f.mutlak_buyukluk(-26.74, 4.8481e-6), 4.83, delta=0.01)

    def test_uzaklik_parsek_gidis_donus(self):
        for d in (1.3, 10.0, 250.0, 1.0e4):
            m = f.mutlak_buyukluk(12.5, d)
            self.assertAlmostEqual(f.uzaklik_parsek(12.5, m), d, delta=d * 1e-12)

    def test_gecersiz(self):
        for kotu in (0, -5, float("nan")):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.uzaklik_modulu(kotu)


class HavaKutlesiTests(unittest.TestCase):
    def test_zenit(self):
        self.assertAlmostEqual(f.hava_kutlesi_sec(0), 1.0, places=12)
        self.assertAlmostEqual(f.hava_kutlesi(0), 1.0, delta=1e-3)

    def test_sec_geometrisi(self):
        # sec(60°) = 2 tam; sec(45°) = sqrt(2).
        self.assertAlmostEqual(f.hava_kutlesi_sec(60), 2.0, places=12)
        self.assertAlmostEqual(f.hava_kutlesi_sec(45), math.sqrt(2.0), places=12)

    def test_kasten_young(self):
        # 60°: sec 2.000'dan biraz küçük (≈1.99); ufukta ≈38 (Kasten ve Young 1989).
        self.assertAlmostEqual(f.hava_kutlesi(60), 1.995, delta=0.01)
        self.assertAlmostEqual(f.hava_kutlesi(90), 38.0, delta=0.5)
        self.assertLess(f.hava_kutlesi(60), f.hava_kutlesi_sec(60))

    def test_artan_ve_sonlu(self):
        degerler = [f.hava_kutlesi(z) for z in range(0, 91, 5)]
        self.assertEqual(degerler, sorted(degerler))
        self.assertTrue(all(math.isfinite(v) for v in degerler))

    def test_gecersiz(self):
        for kotu in (-0.1, 90.1, float("nan"), True, "30"):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.hava_kutlesi(kotu)
        with self.assertRaises(ValueError):
            f.hava_kutlesi_sec(90)


if __name__ == "__main__":
    unittest.main()
