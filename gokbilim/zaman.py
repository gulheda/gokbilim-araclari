"""Astronomide kullanilan zaman donusumleri: Jülyen Günü (JD), değiştirilmiş JD (MJD) ve UTC.

Tüm donusumler UTC takvimi üzerinedir; TT/TDB farkı ve artık saniyeler dikkate alınmaz.
Bu, ZTF gibi uyarı akışlarındaki gözlem zamanlarını okumak için yeterlidir, hassas efemeris için değildir.
"""
from datetime import datetime, timedelta, timezone

JD_UNIX_EPOCH = 2440587.5
MJD_OFFSET = 2400000.5
J2000 = 2451545.0

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _utc(value):
    if value.tzinfo is None:
        raise ValueError("Zaman, saat dilimi içermelidir.")
    return value.astimezone(timezone.utc)


def jd_den_tarihe(jd):
    """Jülyen Günü, saat dilimli UTC datetime'a çevirir."""
    if isinstance(jd, bool) or not isinstance(jd, (int, float)) or jd != jd or jd in (float("inf"), float("-inf")):
        raise ValueError("JD sonlu bir sayı olmalı.")
    return _EPOCH + timedelta(days=jd - JD_UNIX_EPOCH)


def tarihten_jd(tarih):
    """Saat dilimli datetime'ı Jülyen Güne çevirir."""
    return JD_UNIX_EPOCH + (_utc(tarih) - _EPOCH) / timedelta(days=1)


def jd_den_mjd(jd):
    return jd - MJD_OFFSET


def mjd_den_jd(mjd):
    return mjd + MJD_OFFSET


def j2000_den_beri_gun(tarih):
    """J2000.0 (JD 2451545.0) başlangıcından bu yana geçen gün sayısı."""
    return tarihten_jd(tarih) - J2000


def greenwich_yildiz_zamani(tarih):
    """Greenwich ortalama yıldız zamanını (GMST) derece cinsinden döndürür, [0, 360).

    Formül: Meeus, "Astronomical Algorithms", 2. baskı, denklem 12.4.
    Referans: Meeus örnek 12.a — 1987-04-10 0h UT (JD 2446895.5) için GMST = 13h10m46.3668s;
    örnek 12.b — 1987-04-10 19h21m00s UT için GMST = 8h34m57.0896s.
    Girdi UTC olarak ele alınır (UT1-UTC farkı, en çok ~0.9 s, yok sayılır); ortalama yıldız
    zamanıdır, nutasyon düzeltmesi (görünür yıldız zamanı) yoktur.
    """
    jd = tarihten_jd(tarih)
    t = (jd - J2000) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd - J2000)
            + 0.000387933 * t * t - t ** 3 / 38710000.0)
    return gmst % 360.0


def yerel_yildiz_zamani(tarih, boylam):
    """Yerel ortalama yıldız zamanını derece cinsinden döndürür, [0, 360).

    boylam: derece, doğuya doğru pozitif (Ankara ≈ +32.86). LST = GMST + boylam
    (Meeus, Bölüm 12). Hassasiyet GMST ile aynıdır (yaklaşık bir yay saniyesi altı).
    """
    if isinstance(boylam, bool) or not isinstance(boylam, (int, float)) or boylam != boylam \
            or not -180.0 <= boylam <= 180.0:
        raise ValueError("Boylam, -180 ile 180 derece arasında sonlu bir sayı olmalı.")
    return (greenwich_yildiz_zamani(tarih) + boylam) % 360.0


def _bolge(saat_dilimi):
    """IANA saat dilimi adını (ör. "Europe/Istanbul") ZoneInfo'ya çevirir."""
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    if not isinstance(saat_dilimi, str) or not saat_dilimi:
        raise ValueError("Saat dilimi, boş olmayan bir IANA adı olmalı.")
    try:
        return ZoneInfo(saat_dilimi)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        raise ValueError(f"Bilinmeyen saat dilimi: {saat_dilimi!r}")


def utc_den_yerele(tarih, saat_dilimi="Europe/Istanbul"):
    """Saat dilimli bir anı verilen IANA saat diliminin yerel saatine çevirir.

    Referans: Türkiye 2016'dan beri kalıcı UTC+3 kullanır; öncesinde kış EET (UTC+2),
    yaz EEST (UTC+3). Örnek: 2016-01-01 12:00 UTC → 14:00 (+02:00);
    2024-01-01 12:00 UTC → 15:00 (+03:00). Kurallar sistemin tz veritabanından gelir.
    """
    return _utc(tarih).astimezone(_bolge(saat_dilimi))


def yerelden_utc(yerel_tarih, saat_dilimi="Europe/Istanbul"):
    """Saat dilimsiz (duvar saati) yerel zamanı UTC'ye çevirir.

    Yaz saati geçişinde belirsiz/var olmayan saatler zoneinfo'nun varsayılanına
    (fold=0) göre çözülür.
    """
    if yerel_tarih.tzinfo is not None:
        raise ValueError("Yerel zaman, saat dilimsiz (naive) olmalı.")
    return yerel_tarih.replace(tzinfo=_bolge(saat_dilimi)).astimezone(timezone.utc)


def yerel_gun_baslangici(tarih, saat_dilimi="Europe/Istanbul"):
    """Anın düştüğü yerel günün 00:00 anını UTC olarak döndürür.

    Örnek: 2024-06-15 21:30 UTC, Istanbul'da 16 Haziran 00:30'dur; gün başlangıcı
    2024-06-15 21:00 UTC (= 16 Haziran 00:00 +03:00).
    """
    yerel = utc_den_yerele(tarih, saat_dilimi)
    gece_yarisi = yerel.replace(hour=0, minute=0, second=0, microsecond=0, fold=0)
    return gece_yarisi.astimezone(timezone.utc)
