import unittest
from datetime import datetime, timedelta, timezone

from gokbilim import zaman


class ZamanTests(unittest.TestCase):
    def test_bilinen_tarihler(self):
        # J2000.0: 2000-01-01 12:00; Unix başlangıcı: 1970-01-01 00:00 (UTC takvimi).
        self.assertEqual(zaman.tarihten_jd(datetime(2000, 1, 1, 12, tzinfo=timezone.utc)), 2451545.0)
        self.assertEqual(zaman.tarihten_jd(datetime(1970, 1, 1, tzinfo=timezone.utc)), 2440587.5)

    def test_mjd(self):
        self.assertEqual(zaman.jd_den_mjd(2451545.0), 51544.5)
        self.assertEqual(zaman.mjd_den_jd(51544.5), 2451545.0)

    def test_gidis_donus(self):
        tarih = datetime(2019, 6, 13, 5, 10, 55, 4145, tzinfo=timezone.utc)
        geri = zaman.jd_den_tarihe(zaman.tarihten_jd(tarih))
        self.assertLess(abs(geri - tarih), timedelta(milliseconds=1))

    def test_saat_dilimi_normallenir(self):
        istanbul = timezone(timedelta(hours=3))
        self.assertEqual(zaman.tarihten_jd(datetime(2000, 1, 1, 15, tzinfo=istanbul)), 2451545.0)

    def test_saat_dilimsiz_reddedilir(self):
        with self.assertRaises(ValueError):
            zaman.tarihten_jd(datetime(2000, 1, 1, 12))

    def test_gecersiz_jd(self):
        for deger in (float("nan"), float("inf"), True, "2451545"):
            with self.subTest(deger=deger), self.assertRaises(ValueError):
                zaman.jd_den_tarihe(deger)

    def test_j2000_den_beri_gun(self):
        self.assertEqual(zaman.j2000_den_beri_gun(datetime(2000, 1, 2, 12, tzinfo=timezone.utc)), 1.0)

    def test_gmst_meeus_12a(self):
        # Meeus örnek 12.a: 13h10m46.3668s = 197.693195 derece.
        gmst = zaman.greenwich_yildiz_zamani(datetime(1987, 4, 10, tzinfo=timezone.utc))
        self.assertAlmostEqual(gmst, (13 + 10 / 60 + 46.3668 / 3600) * 15, places=5)

    def test_gmst_meeus_12b(self):
        # Meeus örnek 12.b: 1987-04-10 19:21:00 UT için 8h34m57.0896s.
        gmst = zaman.greenwich_yildiz_zamani(datetime(1987, 4, 10, 19, 21, tzinfo=timezone.utc))
        self.assertAlmostEqual(gmst, (8 + 34 / 60 + 57.0896 / 3600) * 15, places=5)

    def test_gmst_saat_dilimsiz_reddedilir(self):
        with self.assertRaises(ValueError):
            zaman.greenwich_yildiz_zamani(datetime(2000, 1, 1))

    def test_yerel_yildiz_zamani(self):
        t = datetime(1987, 4, 10, tzinfo=timezone.utc)
        gmst = zaman.greenwich_yildiz_zamani(t)
        self.assertAlmostEqual(zaman.yerel_yildiz_zamani(t, 0), gmst, places=9)
        self.assertAlmostEqual(zaman.yerel_yildiz_zamani(t, 32.5), (197.693195 + 32.5) % 360, places=5)
        # 360 derece sarması: GMST ~197.69 + 170 -> 7.69
        self.assertAlmostEqual(zaman.yerel_yildiz_zamani(t, 170), 7.693195, places=5)

    def test_gecersiz_boylam(self):
        t = datetime(2000, 1, 1, tzinfo=timezone.utc)
        for deger in (181, -181, float("nan"), True, "10"):
            with self.subTest(deger=deger), self.assertRaises(ValueError):
                zaman.yerel_yildiz_zamani(t, deger)


if __name__ == "__main__":
    unittest.main()
