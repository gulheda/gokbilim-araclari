"""Astronomik sabitler ve birim dönüşümleri (SI tabanlı).

Sabit kaynakları: AU, ışık hızı, h, k_B tam tanımlıdır (IAU 2012 B2; SI 2019). G ve gezegen/Güneş
kütle parametreleri CODATA 2018 ve IAU 2015 B3 nominal değerleridir.
"""
import math

ISIK_HIZI = 299792458.0                      # m/s, tam
BIRIM_AU = 149597870700.0                    # m, tam (IAU 2012)
PARSEK = BIRIM_AU * 648000.0 / math.pi       # m, tanım gereği
GUN = 86400.0                                # s
JULIAN_YILI = 365.25 * GUN                   # s
ISIK_YILI = ISIK_HIZI * JULIAN_YILI          # m, tam

G = 6.67430e-11                              # m^3 kg^-1 s^-2 (CODATA 2018)
GM_GUNES = 1.3271244e20                      # m^3 s^-2 (IAU 2015 nominal)
GM_DUNYA = 3.986004e14                       # m^3 s^-2 (IAU 2015 nominal)
GM_JUPITER = 1.2668653e17                    # m^3 s^-2 (IAU 2015 nominal)
KUTLE_GUNES = GM_GUNES / G                   # kg
KUTLE_DUNYA = GM_DUNYA / G                   # kg
KUTLE_JUPITER = GM_JUPITER / G               # kg
R_GUNES = 6.957e8                            # m (IAU 2015 nominal)
R_DUNYA_EKVATOR = 6.3781e6                   # m (IAU 2015 nominal)
R_DUNYA_ORTALAMA = 6.371e6                   # m
L_GUNES = 3.828e26                           # W (IAU 2015 nominal)
T_GUNES = 5772.0                             # K (IAU 2015 nominal efektif sıcaklık)

H_PLANCK = 6.62607015e-34                    # J s, tam
K_BOLTZMANN = 1.380649e-23                   # J/K, tam
SIGMA_SB = 5.670374419e-8                    # W m^-2 K^-4 (CODATA 2018)
WIEN_SABITI = 2.897771955e-3                 # m K (CODATA 2018)

UZUNLUK = {"m": 1.0, "km": 1e3, "au": BIRIM_AU, "pc": PARSEK, "ly": ISIK_YILI,
           "r_gunes": R_GUNES, "r_dunya": R_DUNYA_EKVATOR}
KUTLE = {"kg": 1.0, "m_gunes": KUTLE_GUNES, "m_dunya": KUTLE_DUNYA, "m_jupiter": KUTLE_JUPITER}
ZAMAN = {"s": 1.0, "dk": 60.0, "saat": 3600.0, "gun": GUN, "yil": JULIAN_YILI}
ACI = {"derece": 1.0, "radyan": 180.0 / math.pi, "yay_dakikasi": 1.0 / 60.0,
       "yay_saniyesi": 1.0 / 3600.0, "mas": 1.0 / 3.6e6}


def _cevir(deger, kaynak, hedef, tablo, tur):
    if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger):
        raise ValueError("Değer sonlu bir sayı olmalı.")
    for birim in (kaynak, hedef):
        if birim not in tablo:
            raise ValueError(f"Bilinmeyen {tur} birimi: {birim!r}. Geçerli: {', '.join(tablo)}")
    return deger * tablo[kaynak] / tablo[hedef]


def uzunluk_cevir(deger, kaynak, hedef):
    """Uzunluk: m, km, au, pc, ly, r_gunes, r_dunya. 1 pc = 648000/π au = 3.2616 ly."""
    return _cevir(deger, kaynak, hedef, UZUNLUK, "uzunluk")


def kutle_cevir(deger, kaynak, hedef):
    """Kütle: kg, m_gunes, m_dunya, m_jupiter (GM değerlerinden, G ile)."""
    return _cevir(deger, kaynak, hedef, KUTLE, "kütle")


def zaman_cevir(deger, kaynak, hedef):
    """Zaman: s, dk, saat, gun (86400 s), yil (Jülyen yılı = 365.25 gün)."""
    return _cevir(deger, kaynak, hedef, ZAMAN, "zaman")


def aci_cevir(deger, kaynak, hedef):
    """Açı: derece, radyan, yay_dakikasi, yay_saniyesi, mas (miliyay saniyesi)."""
    return _cevir(deger, kaynak, hedef, ACI, "açı")
