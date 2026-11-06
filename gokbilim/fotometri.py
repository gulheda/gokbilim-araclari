"""Fotometri yardımcıları: büyüklük–akı ilişkisi, uzaklık modülü, hava kütlesi.

Büyüklük ölçeği logaritmiktir ve ters yönlüdür: küçük büyüklük daha parlaktır.
"""
import math

# Pogson katsayısı: 2.5 / ln(10) ≈ 1.0857; büyüklük hatası = 1.0857 * (akı hatası / akı).
POGSON_HATA_KATSAYISI = 2.5 / math.log(10.0)


def _sonlu(deger, ad):
    if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger):
        raise ValueError(f"{ad} sonlu bir sayı olmalı.")
    return float(deger)


def _pozitif(deger, ad):
    deger = _sonlu(deger, ad)
    if deger <= 0:
        raise ValueError(f"{ad} pozitif olmalı.")
    return deger


def aki_orani(buyukluk1, buyukluk2):
    """F1 / F2 akı oranı, Pogson bağıntısı: m1 - m2 = -2.5 log10(F1 / F2).

    Referans: 5 büyüklük farkı tam olarak 100 kat akı farkıdır (Pogson, 1856);
    1 büyüklük farkı 100**(1/5) ≈ 2.512 kattır. Birinci nesne daha parlaksa oran 1'den büyüktür.
    """
    fark = _sonlu(buyukluk1, "Büyüklük") - _sonlu(buyukluk2, "Büyüklük")
    return 10.0 ** (-0.4 * fark)


def buyukluk_farki(aki1, aki2):
    """m1 - m2 büyüklük farkı; akılar pozitif olmalıdır."""
    return -2.5 * math.log10(_pozitif(aki1, "Akı") / _pozitif(aki2, "Akı"))


def buyukluk_hatasi(aki, aki_hatasi):
    """Akı hatasından büyüklük hatası: sigma_m = 1.0857 * sigma_F / F (küçük hata yaklaşımı)."""
    if _sonlu(aki_hatasi, "Akı hatası") < 0:
        raise ValueError("Akı hatası negatif olamaz.")
    return POGSON_HATA_KATSAYISI * aki_hatasi / _pozitif(aki, "Akı")


def uzaklik_modulu(parsek):
    """m - M = 5 log10(d / 10 pc); yutulma yok sayılır."""
    return 5.0 * math.log10(_pozitif(parsek, "Uzaklık") / 10.0)


def mutlak_buyukluk(gorunur_buyukluk, parsek):
    """M = m - 5 log10(d / 10 pc).

    Referans: Güneş, V bandında m = -26.74 ve 1 AU = 4.8481e-6 pc uzaklıkta
    M = 4.83 verir (m - M = -31.57).
    """
    return _sonlu(gorunur_buyukluk, "Görünür büyüklük") - uzaklik_modulu(parsek)


def uzaklik_parsek(gorunur_buyukluk, mutlak):
    """d = 10 ** ((m - M + 5) / 5) parsek; yutulma yok sayılır."""
    return 10.0 ** ((_sonlu(gorunur_buyukluk, "Görünür büyüklük") - _sonlu(mutlak, "Mutlak büyüklük") + 5.0) / 5.0)


def hava_kutlesi_sec(zenit_acisi):
    """Düzlem-paralel atmosfer: X = sec(z). z < 80° için kullanın; ufka yakın aşırı büyür."""
    z = _zenit(zenit_acisi)
    if z >= 90.0:
        raise ValueError("Düzlem-paralel hava kütlesi ufukta tanımsızdır; Kasten–Young kullanın.")
    return 1.0 / math.cos(math.radians(z))


def hava_kutlesi(zenit_acisi):
    """Kasten ve Young (1989) hava kütlesi; ufka kadar (z = 90°) tanımlıdır.

    X = 1 / (cos z + 0.50572 * (96.07995 - z)**-1.6364), z derece cinsinden.
    Referans: ufukta X ≈ 38 (formül 37.9 verir); zenitte X ≈ 1.
    """
    z = _zenit(zenit_acisi)
    return 1.0 / (math.cos(math.radians(z)) + 0.50572 * (96.07995 - z) ** -1.6364)


def _zenit(zenit_acisi):
    z = _sonlu(zenit_acisi, "Zenit açısı")
    if not 0.0 <= z <= 90.0:
        raise ValueError("Zenit açısı 0 ile 90 derece arasında olmalı.")
    return z
