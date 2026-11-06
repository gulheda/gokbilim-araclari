import contextlib
import io
import unittest

from gokbilim.__main__ import main


def calistir(*argv):
    cikti = io.StringIO()
    kod = main(list(argv), cikis=cikti)
    return kod, cikti.getvalue()


class KomutSatiriTests(unittest.TestCase):
    def test_jd(self):
        kod, cikti = calistir("jd", "2000-01-01T12:00:00Z")
        self.assertEqual(kod, 0)
        self.assertIn("JD  2451545.000000", cikti)
        self.assertIn("MJD 51544.500000", cikti)

    def test_koordinat_pollux(self):
        _, cikti = calistir("koordinat", "7h45m18.946s", "+28:01:34.26")
        self.assertIn("λ 113.21562", cikti)
        self.assertIn("β +6.68417", cikti)

    def test_ayrim_eksi_dec_deger_olarak_okunur(self):
        # Meeus 17.a: güneydeki Spica'nın Dec'i eksi işaretle başlar.
        _, cikti = calistir("ayrim", "14h15m39.7s", "+19:10:57", "13h25m11.6s", "-11:09:41")
        self.assertEqual(cikti.strip(), "32.793010°")

    def test_eksi_sifir_derece(self):
        _, cikti = calistir("koordinat", "10", "-00:30:00")
        self.assertIn("Dec -0.500000°", cikti)

    def test_gunes(self):
        _, cikti = calistir("gunes", "--yer", "41.01,28.98", "--tarih", "2026-11-07")
        self.assertIn("Doğuş                   2026-11-07 04:41 UTC", cikti)
        self.assertIn("Batış                   2026-11-07 14:53 UTC", cikti)

    def test_kutup_gecesi(self):
        _, cikti = calistir("gunes", "--yer", "69.65,18.96", "--tarih", "2026-12-21")
        self.assertIn("yok (kutup gecesi", cikti)

    def test_hava_kutlesi(self):
        self.assertEqual(calistir("hava-kutlesi", "60")[1].strip(), "1.9943")

    def test_hatalar_cikis_kodu_2(self):
        for argv in (("jd", "2000-01-01"), ("jd", "bozuk"), ("koordinat", "25h", "0"),
                     ("koordinat", "abc", "0"), ("gunes", "--yer", "41"), ("gunes", "--yer", "95,0"),
                     ("hava-kutlesi", "120"), ("yok",), ()):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit) as baglam:
                calistir(*argv)
            self.assertEqual(baglam.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
