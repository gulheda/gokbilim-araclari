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


if __name__ == "__main__":
    unittest.main()
