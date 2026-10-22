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
