"""Gözlem planlama: Güneş'in yaklaşık konumu, yüksekliği, doğuş/batış ve alacakaranlık.

Güneş konumu Meeus, "Astronomical Algorithms" (2. baskı) Bölüm 25'teki düşük doğruluklu
formüllerdir (~0.01°); ΔT (TT-UT ≈ 69 s) yok sayılır, bu Güneş için ~0.001°'dir.
Doğuş/batış zamanlarında beklenen doğruluk yaklaşık 1 dakikadır. Atmosfer kırılması yalnız
standart ufuk yüksekliği (-0.8333°) içinde hesaba katılır; yerel ufuk engelleri yoktur.
"""
import math
from datetime import datetime, timedelta, timezone

from . import koordinat, zaman

# Güneş merkezinin yüksekliği: üst kenar ufukta + standart kırılma (34′ + 16′ yarıçap).
GUNES_UFKU = -0.8333
SIVIL_ALACAKARANLIK = -6.0
DENIZCILIK_ALACAKARANLIGI = -12.0
ASTRONOMIK_ALACAKARANLIK = -18.0

_SIDERAL_GUN_DERECE = 360.98564736629  # bir gündeki yıldız zamanı artışı


def gunes_konumu(tarih):
    """Güneş'in görünür (RA, Dec, uzaklık) değerini döndürür: derece, derece, AU.

    Referans: Meeus örnek 25.a — 1992-10-13 0h (JD 2448908.5): RA = 198.38083°,
    Dec = −7.78507°, R = 0.99766 AU. Nutasyon ve sapma kısaltılmış terimlerle dahildir.
    """
    t = (zaman.tarihten_jd(tarih) - zaman.J2000) / 36525.0
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360.0)
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m) + 0.000289 * math.sin(3 * m))
    gercek_anomali = m + math.radians(c)
    uzaklik = 1.000001018 * (1 - e * e) / (1 + e * math.cos(gercek_anomali))
    omega = math.radians(125.04 - 1934.136 * t)
    boylam = math.radians(l0 + c - 0.00569 - 0.00478 * math.sin(omega))
    egiklik0 = 23 + 26 / 60 + 21.448 / 3600 - (46.8150 * t + 0.00059 * t * t - 0.001813 * t ** 3) / 3600
    egiklik = math.radians(egiklik0 + 0.00256 * math.cos(omega))
    ra = math.degrees(math.atan2(math.cos(egiklik) * math.sin(boylam), math.cos(boylam))) % 360.0
    dec = math.degrees(math.asin(math.sin(egiklik) * math.sin(boylam)))
    return ra, dec, uzaklik


def gunes_yuksekligi(tarih, enlem, boylam):
    """Güneş merkezinin geometrik yüksekliği (derece), belirtilen yerde ve anda."""
    ra, dec, _ = gunes_konumu(tarih)
    return koordinat.ekvatordan_ufka(ra, dec, tarih, enlem, boylam)[1]


def _sar(derece):
    """Açıyı [-180, 180) aralığına sarar."""
    return (derece + 180.0) % 360.0 - 180.0


def _saat_acisi(tarih, boylam):
    ra, dec, _ = gunes_konumu(tarih)
    return _sar(zaman.yerel_yildiz_zamani(tarih, boylam) - ra), dec


def gunes_olaylari(gun, enlem, boylam, yukseklik=GUNES_UFKU):
    """Güneş'in yükselişini, tepe noktasını ve batışını döndürür: (yukselis, tepe, batis).

    gun: Güneş'in tepe noktasından geçtiği UTC takvim günü (datetime.date ya da saat dilimli
    datetime). Doğuş, tepeden önceki; batış, tepeden sonraki anıdır. Çok doğuda olan yerlerde
    doğuş bir önceki UTC gününe düşebilir. yukseklik, Güneş merkezinin derece cinsinden
    hedef yüksekliğidir (varsayılan: doğuş/batış; alacakaranlık için sabitler).
    Güneş o yükseklikten hiç geçmiyorsa (kutup gecesi/geceyarısı güneşi) doğuş ve batış None olur.

    Referans: ABD Deniz Gözlemevi (USNO) servisi, 2026-11-07 İstanbul (41.01 K, 28.98 D):
    doğuş 04:42, tepe 09:48, batış 14:53 UTC; doğruluk testlerde ±2 dakika.
    """
    enlem = koordinat._dec(enlem)
    if isinstance(boylam, bool) or not isinstance(boylam, (int, float)) or not -180.0 <= boylam <= 180.0:
        raise ValueError("Boylam, -180 ile 180 derece arasında sonlu bir sayı olmalı.")
    if not isinstance(yukseklik, (int, float)) or isinstance(yukseklik, bool) or not -90.0 < yukseklik < 90.0:
        raise ValueError("Yükseklik, -90 ile 90 derece arasında olmalı.")
    if isinstance(gun, datetime):
        gun = zaman._utc(gun).date()
    baslangic = datetime(gun.year, gun.month, gun.day, tzinfo=timezone.utc)

    t = baslangic + timedelta(hours=12.0 - boylam / 15.0)
    for _ in range(5):
        saat_acisi, _dec = _saat_acisi(t, boylam)
        t -= timedelta(days=saat_acisi / _SIDERAL_GUN_DERECE)
    tepe = t

    def olay(isaret):
        ara = tepe
        for _ in range(6):
            _, dec = _saat_acisi(ara, boylam)
            phi, d, h0 = math.radians(enlem), math.radians(dec), math.radians(yukseklik)
            cos_h = (math.sin(h0) - math.sin(phi) * math.sin(d)) / (math.cos(phi) * math.cos(d))
            if not -1.0 <= cos_h <= 1.0:
                return None
            hedef = isaret * math.degrees(math.acos(cos_h))
            saat_acisi, _ = _saat_acisi(ara, boylam)
            ara -= timedelta(days=_sar(saat_acisi - hedef) / _SIDERAL_GUN_DERECE)
        return ara

    return olay(-1.0), tepe, olay(+1.0)
