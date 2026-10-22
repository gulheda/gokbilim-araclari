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
