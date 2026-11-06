"""Gök koordinatı yardımcıları: RA/Dec biçimleri, ayrıştırma, açısal uzaklık, galaktik dönüşüm.

Tüm açılar derece cinsindedir. RA [0, 360), Dec [-90, 90]. Epok J2000 varsayılır;
presesyon, nutasyon ve özhareket dikkate alınmaz.
"""
import math
import re

from . import zaman

_SAYI = re.compile(r"\d+(?:\.\d+)?")


def _sonlu(deger, ad):
    if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger):
        raise ValueError(f"{ad} sonlu bir sayı olmalı.")
    return float(deger)


def _ra(ra):
    ra = _sonlu(ra, "RA")
    if not 0.0 <= ra < 360.0:
        raise ValueError("RA, [0, 360) derece aralığında olmalı.")
    return ra


def _dec(dec):
    dec = _sonlu(dec, "Dec")
    if not -90.0 <= dec <= 90.0:
        raise ValueError("Dec, [-90, 90] derece aralığında olmalı.")
    return dec


# --- Biçimler -------------------------------------------------------------

def ra_hms(derece):
    """RA'yı (saat, dakika, saniye) olarak verir; saniye 0.001 s'ye yuvarlanır.

    15 derece = 1 saat. Örnek (Meeus 12.a): 197.693195° ≈ 13h10m46.367s.
    Yuvarlama 24h'ye taşarsa 0h'a sarılır.
    """
    toplam_ms = round(_ra(derece) / 15.0 * 3600.0 * 1000.0) % (24 * 3600 * 1000)
    saat, kalan = divmod(toplam_ms, 3600 * 1000)
    dakika, ms = divmod(kalan, 60 * 1000)
    return saat, dakika, ms / 1000.0


def dec_dms(derece):
    """Dec'i (işaret, derece, yay dakikası, yay saniyesi) olarak verir; saniye 0.001″'ye yuvarlanır.

    İşaret "+" veya "-" metnidir; böylece -00:30:00 gibi değerler kaybolmaz.
    """
    dec = _dec(derece)
    toplam_mas = round(abs(dec) * 3600.0 * 1000.0)
    d, kalan = divmod(toplam_mas, 3600 * 1000)
    dk, mas = divmod(kalan, 60 * 1000)
    isaret = "-" if dec < 0 and toplam_mas > 0 else "+"
    return isaret, d, dk, mas / 1000.0


def ra_metni(derece):
    s, d, sn = ra_hms(derece)
    return f"{s:02d}:{d:02d}:{sn:06.3f}"


def dec_metni(derece):
    isaret, d, dk, sn = dec_dms(derece)
    return f"{isaret}{d:02d}:{dk:02d}:{sn:06.3f}"


# --- Ayrıştırma -----------------------------------------------------------

def _parcalar(metin, ad):
    if not isinstance(metin, str):
        raise ValueError(f"{ad} metin olmalı.")
    parcalar = re.sub(r"[hdms°′″'\":]", " ", metin.strip().lower()).split()
    if not 1 <= len(parcalar) <= 3 or any(not _SAYI.fullmatch(p) for p in parcalar):
        raise ValueError(f"Geçersiz {ad} biçimi: {metin!r}")
    if any("." in p for p in parcalar[:-1]):
        raise ValueError(f"Yalnız son bileşen ondalıklı olabilir: {metin!r}")
    return [float(p) for p in parcalar]


def _altmis(degerler, metin):
    if any(v >= 60 for v in degerler[1:]):
        raise ValueError(f"Dakika ve saniye 60'tan küçük olmalı: {metin!r}")


def ra_ayristir(metin):
    """RA metnini dereceye çevirir.

    Saat biçimi: "12h30m45.5s", "12:30:45.5", "12 30 45.5", "12h30m". Tek sayı veya
    "d"/"°" içeren metin derece sayılır ("187.5", "187.5°"). Sonuç [0, 360) olmalıdır.
    """
    derece_mi = bool(re.search(r"[d°]", str(metin).lower()))
    parcalar = _parcalar(metin, "RA")
    if derece_mi or len(parcalar) == 1 and not re.search(r"[h:]", metin.lower()):
        if len(parcalar) != 1:
            raise ValueError(f"Geçersiz RA biçimi: {metin!r}")
        sonuc = parcalar[0]
    else:
        _altmis(parcalar, metin)
        saat = sum(v / 60.0 ** i for i, v in enumerate(parcalar))
        sonuc = saat * 15.0
    if not 0.0 <= sonuc < 360.0:
        raise ValueError(f"RA, [0, 360) derece aralığında olmalı: {metin!r}")
    return sonuc


def dec_ayristir(metin):
    """Dec metnini dereceye çevirir.

    "+45:30:15", "-00:30:00", "45d30m15s", "+45°30′15″", "-12.5". İşaret ayrı okunur,
    böylece "-00:30:00" doğru biçimde -0.5° olur. Sonuç [-90, 90] olmalıdır.
    """
    if not isinstance(metin, str):
        raise ValueError("Dec metin olmalı.")
    kirpik = metin.strip().replace("−", "-")
    isaret = -1.0 if kirpik.startswith("-") else 1.0
    parcalar = _parcalar(kirpik.lstrip("+-"), "Dec")
    _altmis(parcalar, metin)
    sonuc = isaret * sum(v / 60.0 ** i for i, v in enumerate(parcalar))
    if not -90.0 <= sonuc <= 90.0:
        raise ValueError(f"Dec, [-90, 90] derece aralığında olmalı: {metin!r}")
    return sonuc


# --- Açısal uzaklık -------------------------------------------------------

def aci_uzakligi(ra1, dec1, ra2, dec2):
    """İki nokta arasındaki açıyı derece olarak verir (haversine).

    Küçük açılarda kararlıdır. Referans: Meeus, "Astronomical Algorithms", Bölüm 17,
    örnek 17.a: Arcturus (14h15m39.7s, +19°10′57″) – Spica (13h25m11.6s, −11°09′41″) = 32.7930°.
    """
    a1, d1, a2, d2 = (math.radians(v) for v in (_ra(ra1), _dec(dec1), _ra(ra2), _dec(dec2)))
    hav = math.sin((d2 - d1) / 2) ** 2 + math.cos(d1) * math.cos(d2) * math.sin((a2 - a1) / 2) ** 2
    return math.degrees(2.0 * math.asin(min(1.0, math.sqrt(hav))))


def _birim_vektor(ra, dec):
    a, d = math.radians(_ra(ra)), math.radians(_dec(dec))
    return math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d)


def aci_uzakligi_vektor(ra1, dec1, ra2, dec2):
    """Aynı uzaklığı atan2(|a×b|, a·b) ile hesaplar; ters (180°) noktalarda da kararlıdır."""
    a, b = _birim_vektor(ra1, dec1), _birim_vektor(ra2, dec2)
    carpim = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    return math.degrees(math.atan2(math.sqrt(sum(c * c for c in carpim)),
                                   sum(x * y for x, y in zip(a, b))))


# --- Galaktik dönüşüm -----------------------------------------------------

# Ekvatordan galaktiğe J2000 dönüşüm matrisi (ESA, Hipparcos ve Tycho Kataloğu, 1997, Cilt 1, Böl. 1.5.3).
_EKV_GAL = ((-0.0548755604, -0.8734370902, -0.4838350155),
            (0.4941094279, -0.4448296300, 0.7469822445),
            (-0.8676661490, -0.1980763734, 0.4559837762))


def ekvatordan_galaktige(ra, dec):
    """J2000 (RA, Dec) → galaktik (l, b), derece. l [0, 360), b [-90, 90].

    Enlem atan2 ile hesaplanır; böylece kutba yakın noktalarda asin'in hassasiyet kaybı olmaz.
    Matris 10 haneli olduğundan sonuç yaklaşık 1e-7 derece (0.0004″) doğrudur.
    """
    v = _birim_vektor(ra, dec)
    g = [sum(m * x for m, x in zip(satir, v)) for satir in _EKV_GAL]
    l = math.degrees(math.atan2(g[1], g[0])) % 360.0
    b = math.degrees(math.atan2(g[2], math.hypot(g[0], g[1])))
    return l, b


def galaktikten_ekvatora(l, b):
    """Galaktik (l, b) → J2000 (RA, Dec), derece. Dönüşüm matrisinin devriğini kullanır."""
    l, b = _sonlu(l, "l"), _dec(b)
    if not 0.0 <= l < 360.0:
        raise ValueError("l, [0, 360) derece aralığında olmalı.")
    lr, br = math.radians(l), math.radians(b)
    g = (math.cos(br) * math.cos(lr), math.cos(br) * math.sin(lr), math.sin(br))
    e = [sum(_EKV_GAL[j][i] * g[j] for j in range(3)) for i in range(3)]
    ra = math.degrees(math.atan2(e[1], e[0])) % 360.0
    dec = math.degrees(math.atan2(e[2], math.hypot(e[0], e[1])))
    return ra, dec


# --- Ufuk koordinatları ---------------------------------------------------

def ekvatordan_ufka(ra, dec, tarih, enlem, boylam):
    """Ekvator (RA, Dec) → ufuk (azimut, yükseklik), derece.

    Azimut kuzeyden doğuya doğru ölçülür (K=0, D=90, G=180, B=270); Meeus güneyden
    batıya ölçer, aradaki fark 180°'dir. Enlem ve doğu pozitif boylam derecedir.
    Referans: Meeus, Bölüm 13, örnek 13.b — Venüs (RA 23h09m16.641s, Dec −6°43′11.61″),
    Washington (enlem +38°55′17″, boylam 77°03′56″ B), 1987-04-10 19:21 UT için
    Meeus azimut 68.0337° (güneyden), yükseklik +15.1249° verir; bu fonksiyon 248.034°, 15.124°.
    ~0.0006°'lik fark Meeus'un görünür yıldız zamanı (nutasyonlu) kullanmasındandır; burada
    ortalama yıldız zamanı kullanılır. Kırılma düzeltmesi yoktur (geometrik yükseklik).
    """
    ra, dec, enlem = _ra(ra), _dec(dec), _dec(enlem)
    h = math.radians(zaman.yerel_yildiz_zamani(tarih, boylam) - ra)
    phi, d = math.radians(enlem), math.radians(dec)
    # Ufuk çerçevesinde bileşenler: güney, batı, zenit. atan2 zenit ve ufuk yakınında asin'den kararlıdır.
    guney = math.cos(d) * math.cos(h) * math.sin(phi) - math.sin(d) * math.cos(phi)
    bati = math.cos(d) * math.sin(h)
    zenit = math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(h)
    guneyden = math.atan2(bati, guney)
    yukseklik = math.degrees(math.atan2(zenit, math.hypot(guney, bati)))
    return (math.degrees(guneyden) + 180.0) % 360.0, yukseklik
