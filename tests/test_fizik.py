import math
import unittest

from gokbilim import birimler as b
from gokbilim import fizik as f

GUN = 86400.0


class KeplerTests(unittest.TestCase):
    def test_gauss_yili(self):
        # 2π/k, k = 0.01720209895 (Gauss sabiti) => 365.2568983 gün.
        donem = f.kepler_donemi(b.BIRIM_AU, b.KUTLE_GUNES) / GUN
        self.assertAlmostEqual(donem, 365.2568983, delta=0.001)

    def test_mars(self):
        # Gözlenen yıldız dönemi 686.98 gün (a = 1.523679 AU); Güneş-yalnız yaklaşımı ≈0.01 gün düşük.
        donem = f.kepler_donemi(1.523679 * b.BIRIM_AU, b.KUTLE_GUNES) / GUN
        self.assertAlmostEqual(donem, 686.98, delta=0.02)

    def test_jupiter_toplam_kutle(self):
        # Gözlenen 4332.6 gün; Güneş+Jüpiter toplam kütlesiyle %0.01 içinde, yalnız Güneş'le %0.04 sapar.
        a = 5.2026 * b.BIRIM_AU
        toplam = f.kepler_donemi(a, b.KUTLE_GUNES + b.KUTLE_JUPITER) / GUN
        yalniz_gunes = f.kepler_donemi(a, b.KUTLE_GUNES) / GUN
        self.assertAlmostEqual(toplam, 4332.6, delta=0.6)
        self.assertGreater(yalniz_gunes - toplam, 1.5)

    def test_kutle_arttikca_donem_kisalir(self):
        self.assertLess(f.kepler_donemi(1e11, 4e30), f.kepler_donemi(1e11, 2e30))

    def test_yorunge_hizi(self):
        self.assertAlmostEqual(f.dairesel_yorunge_hizi(b.BIRIM_AU, b.KUTLE_GUNES) / 1e3, 29.78, delta=0.01)


class KacisVeKutleCekimiTests(unittest.TestCase):
    def test_kacis_hizlari(self):
        self.assertAlmostEqual(f.kacis_hizi(b.R_DUNYA_ORTALAMA, b.KUTLE_DUNYA) / 1e3, 11.19, delta=0.01)
        # Ay: GM = 4.9028e12 m^3/s^2, R = 1737.4 km  =>  2.38 km/s.
        self.assertAlmostEqual(f.kacis_hizi(1.7374e6, 4.9028e12 / b.G) / 1e3, 2.38, delta=0.01)

    def test_kacis_ve_dairesel_orani(self):
        self.assertAlmostEqual(f.kacis_hizi(7e6, 6e24) / f.dairesel_yorunge_hizi(7e6, 6e24), math.sqrt(2.0), places=12)

    def test_schwarzschild(self):
        self.assertAlmostEqual(f.schwarzschild_yaricapi(b.KUTLE_GUNES) / 1e3, 2.953, delta=0.001)
        # Dünya ≈ 8.87 mm.
        self.assertAlmostEqual(f.schwarzschild_yaricapi(b.KUTLE_DUNYA) * 1e3, 8.87, delta=0.01)


class DopplerHubbleTests(unittest.TestCase):
    def test_z_bir(self):
        self.assertAlmostEqual(f.kirmizi_kayma_hizi(1.0) / b.ISIK_HIZI, 0.6, places=12)

    def test_kucuk_z_klasik_yaklasim(self):
        self.assertAlmostEqual(f.kirmizi_kayma_hizi(0.001) / b.ISIK_HIZI, 0.001, delta=1e-6)

    def test_negatif_z_mavi_kayma(self):
        self.assertLess(f.kirmizi_kayma_hizi(-0.5), 0)
        self.assertEqual(f.kirmizi_kayma_hizi(0.0), 0.0)

    def test_z_gecersiz(self):
        for kotu in (-1.0, -2, float("nan"), float("inf"), True, "1"):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.kirmizi_kayma_hizi(kotu)

    def test_hubble(self):
        self.assertEqual(f.hubble_hizi(100.0, 70.0), 7000.0)
        with self.assertRaises(ValueError):
            f.hubble_hizi(100.0, 0)


class IsinimTests(unittest.TestCase):
    def test_wien(self):
        self.assertAlmostEqual(f.wien_dalga_boyu(b.T_GUNES) * 1e9, 502.0, delta=0.1)
        self.assertAlmostEqual(f.wien_dalga_boyu(2.725) * 1e3, 1.063, delta=0.001)

    def test_gunes_isinim_gucu(self):
        # IAU 2015 nominal değerleri birbirini doğrular: R = 6.957e8 m, T = 5772 K  =>  L = 3.828e26 W.
        self.assertAlmostEqual(f.isinim_gucu(b.R_GUNES, b.T_GUNES) / b.L_GUNES, 1.0, delta=1e-5)
        self.assertAlmostEqual(f.etkin_sicaklik(b.L_GUNES, b.R_GUNES), b.T_GUNES, delta=0.01)

    def test_olcekleme(self):
        # Sıcaklık iki katına çıkarsa güç 16 kat, yarıçap iki katına çıkarsa 4 kat artar.
        temel = f.isinim_gucu(1e8, 5000)
        self.assertAlmostEqual(f.isinim_gucu(1e8, 10000) / temel, 16.0, places=9)
        self.assertAlmostEqual(f.isinim_gucu(2e8, 5000) / temel, 4.0, places=9)

    def test_gecersiz(self):
        for kotu in (0, -1, float("nan"), True, None):
            with self.subTest(kotu=kotu), self.assertRaises(ValueError):
                f.wien_dalga_boyu(kotu)
        with self.assertRaises(ValueError):
            f.isinim_gucu(-1, 5000)
        with self.assertRaises(ValueError):
            f.kepler_donemi(1e11, 0)


if __name__ == "__main__":
    unittest.main()
