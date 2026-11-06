"""Temel astrofizik formülleri; tüm girdi ve çıktılar SI birimindedir (m, kg, s, K, W).

Birim dönüşümü için gokbilim.birimler kullanın. Newton mekaniği geçerlidir (genel görelilik
düzeltmesi yok); Schwarzschild yarıçapı ve göreli Doppler bu kuralın istisnalarıdır.
"""
import math

from .birimler import (G, ISIK_HIZI, SIGMA_SB, WIEN_SABITI)


def _pozitif(deger, ad):
    if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger) or deger <= 0:
        raise ValueError(f"{ad} pozitif ve sonlu bir sayı olmalı.")
    return float(deger)


def kepler_donemi(yari_buyuk_eksen, toplam_kutle):
    """Yörünge dönemi (s): P = 2π sqrt(a³ / (G M)); Kepler'in üçüncü yasası (Newton biçimi).

    Toplam kütle (merkez + yörüngedeki cisim) verilmelidir; Jüpiter gibi kütleli cisimlerde bu
    fark yaklaşık %0.05'tir. Referans: Dünya (a = 1 AU, M = Güneş) için Gauss yılı 365.2569 gün;
    Mars (a = 1.523679 AU) için gözlenen yıldız dönemi 686.98 gün (bu fonksiyon 686.97); Jüpiter
    (a = 5.2026 AU) için gözlenen 4332.6 gün (Güneş+Jüpiter kütlesiyle 4332.3; yalnız Güneş'le 4334.4).
    """
    a, m = _pozitif(yari_buyuk_eksen, "Yarı büyük eksen"), _pozitif(toplam_kutle, "Kütle")
    return 2.0 * math.pi * math.sqrt(a ** 3 / (G * m))


def dairesel_yorunge_hizi(yaricap, merkez_kutle):
    """Dairesel yörünge hızı (m/s): v = sqrt(G M / r). Dünya için ≈ 29.78 km/s."""
    return math.sqrt(G * _pozitif(merkez_kutle, "Kütle") / _pozitif(yaricap, "Yarıçap"))


def kacis_hizi(yaricap, kutle):
    """Kaçış hızı (m/s): v = sqrt(2 G M / r). Dünya yüzeyi için ≈ 11.19 km/s, Ay için ≈ 2.38 km/s."""
    return math.sqrt(2.0 * G * _pozitif(kutle, "Kütle") / _pozitif(yaricap, "Yarıçap"))


def schwarzschild_yaricapi(kutle):
    """Rs = 2 G M / c² (m). Güneş kütlesi için ≈ 2.95 km."""
    return 2.0 * G * _pozitif(kutle, "Kütle") / ISIK_HIZI ** 2


def kirmizi_kayma_hizi(z):
    """Göreli Doppler: v = c ((1+z)² − 1) / ((1+z)² + 1) (m/s), z > −1.

    Referans: z = 1 için v/c = 3/5 tam olarak. Kozmolojik genişleme değil, yalnız Doppler
    yorumudur; büyük z'de yerel hız anlamı taşımaz.
    """
    if isinstance(z, bool) or not isinstance(z, (int, float)) or not math.isfinite(z) or z <= -1.0:
        raise ValueError("Kırmızıya kayma sonlu ve -1'den büyük olmalı.")
    k = (1.0 + z) ** 2
    return ISIK_HIZI * (k - 1.0) / (k + 1.0)


def hubble_hizi(uzaklik_mpc, h0):
    """Hubble yasası: v = H0 d (km/s). uzaklik Mpc, h0 km/s/Mpc; yakın evrende geçerlidir."""
    return _pozitif(h0, "H0") * _pozitif(uzaklik_mpc, "Uzaklık")


def wien_dalga_boyu(sicaklik):
    """Siyah cismin tepe dalga boyu (m): λmax = b / T. Güneş (5772 K) için ≈ 502 nm, CMB (2.725 K) için ≈ 1.063 mm."""
    return WIEN_SABITI / _pozitif(sicaklik, "Sıcaklık")


def isinim_gucu(yaricap, sicaklik):
    """Küresel siyah cisim ışınım gücü (W): L = 4π R² σ T⁴. Güneş (6.957e8 m, 5772 K) için ≈ 3.828e26 W."""
    return 4.0 * math.pi * _pozitif(yaricap, "Yarıçap") ** 2 * SIGMA_SB * _pozitif(sicaklik, "Sıcaklık") ** 4


def etkin_sicaklik(isinim, yaricap):
    """Işınım gücü ve yarıçaptan etkin sıcaklık (K): T = (L / (4π R² σ))^(1/4)."""
    return (_pozitif(isinim, "Işınım gücü") / (4.0 * math.pi * _pozitif(yaricap, "Yarıçap") ** 2 * SIGMA_SB)) ** 0.25
