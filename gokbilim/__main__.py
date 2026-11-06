"""Komut satırı: python -m gokbilim {jd,koordinat,ayrim,gunes} ..."""
import argparse
import re
import sys
from datetime import date, datetime, timezone

from . import fotometri, gozlem, koordinat, zaman


def _an(metin):
    try:
        an = datetime.fromisoformat(metin.replace("Z", "+00:00"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Geçersiz zaman: {metin!r} (örnek: 2026-11-07T12:00:00Z)")
    if an.tzinfo is None:
        raise argparse.ArgumentTypeError("Zaman saat dilimi içermeli (örnek: 2026-11-07T12:00:00Z)")
    return an


def _gun(metin):
    try:
        return date.fromisoformat(metin)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Geçersiz tarih: {metin!r} (örnek: 2026-11-07)")


def _yer(metin):
    try:
        enlem, boylam = (float(parca) for parca in metin.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Geçersiz yer: {metin!r} (örnek: 41.01,28.98 = enlem,doğu boylamı)")
    return enlem, boylam


def _saat(an):
    return an.strftime("%Y-%m-%d %H:%M UTC") if an else "yok (kutup gecesi/gece yarısı güneşi)"


# "-11:09:41" ve "-26d25m55s" gibi eksi işaretli Dec değerleri seçenek değil, değerdir.
_EKSI_DEGER = re.compile(r"^-\d[\d:.dms]*$")


def _parser():
    ana = argparse.ArgumentParser(prog="gokbilim", description="Gökbilim hesap yardımcıları")
    alt = ana.add_subparsers(dest="komut", required=True)
    ekle = alt.add_parser

    def alt_komut(*a, **k):
        p = ekle(*a, **k)
        p._negative_number_matcher = _EKSI_DEGER
        return p
    alt.add_parser = alt_komut
    p = alt.add_parser("jd", help="Zamanı Jülyen Güne çevir")
    p.add_argument("zaman", type=_an)
    p = alt.add_parser("koordinat", help="RA/Dec'i ondalık, galaktik ve ekliptik olarak göster")
    p.add_argument("ra", help='ör. "12h30m45s" veya 187.5')
    p.add_argument("dec", help='ör. "+45:30:15"')
    p = alt.add_parser("ayrim", help="İki nokta arası açısal uzaklık")
    for ad in ("ra1", "dec1", "ra2", "dec2"):
        p.add_argument(ad)
    p = alt.add_parser("gunes", help="Güneş doğuş/tepe/batış ve alacakaranlık (UTC)")
    p.add_argument("--yer", type=_yer, required=True, help="enlem,boylam (doğu pozitif)")
    p.add_argument("--tarih", type=_gun, default=None, help="UTC günü, varsayılan bugün")
    p = alt.add_parser("hava-kutlesi", help="Zenit açısından hava kütlesi")
    p.add_argument("zenit", type=float)
    return ana


def main(argv=None, cikis=None):
    cikis = cikis or sys.stdout
    ana = _parser()
    args = ana.parse_args(argv)
    yaz = lambda satir: print(satir, file=cikis)
    try:
        if args.komut == "jd":
            jd = zaman.tarihten_jd(args.zaman)
            yaz(f"JD  {jd:.6f}")
            yaz(f"MJD {zaman.jd_den_mjd(jd):.6f}")
        elif args.komut == "koordinat":
            ra, dec = koordinat.ra_ayristir(args.ra), koordinat.dec_ayristir(args.dec)
            l, b = koordinat.ekvatordan_galaktige(ra, dec)
            lam, beta = koordinat.ekvatordan_ekliptige(ra, dec)
            yaz(f"Ekvator   RA {ra:.6f}° ({koordinat.ra_metni(ra)})  Dec {dec:+.6f}° ({koordinat.dec_metni(dec)})")
            yaz(f"Galaktik  l {l:.6f}°  b {b:+.6f}°")
            yaz(f"Ekliptik  λ {lam:.6f}°  β {beta:+.6f}°")
        elif args.komut == "ayrim":
            nokta = (koordinat.ra_ayristir(args.ra1), koordinat.dec_ayristir(args.dec1),
                     koordinat.ra_ayristir(args.ra2), koordinat.dec_ayristir(args.dec2))
            yaz(f"{koordinat.aci_uzakligi(*nokta):.6f}°")
        elif args.komut == "gunes":
            gun = args.tarih or datetime.now(timezone.utc).date()
            enlem, boylam = args.yer
            yukselis, tepe, batis = gozlem.gunes_olaylari(gun, enlem, boylam)
            sivil = gozlem.gunes_olaylari(gun, enlem, boylam, gozlem.SIVIL_ALACAKARANLIK)
            yaz(f"Sivil alacakaranlık başı {_saat(sivil[0])}")
            yaz(f"Doğuş                   {_saat(yukselis)}")
            yaz(f"Tepe                    {_saat(tepe)}")
            yaz(f"Batış                   {_saat(batis)}")
            yaz(f"Sivil alacakaranlık sonu {_saat(sivil[2])}")
        elif args.komut == "hava-kutlesi":
            yaz(f"{fotometri.hava_kutlesi(args.zenit):.4f}")
    except ValueError as hata:
        ana.error(str(hata))
    return 0


if __name__ == "__main__":
    sys.exit(main())
