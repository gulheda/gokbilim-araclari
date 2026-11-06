# gökbilim-araçları

[![Tests](https://github.com/gulheda/gokbilim-araclari/actions/workflows/tests.yml/badge.svg)](https://github.com/gulheda/gokbilim-araclari/actions/workflows/tests.yml)

Gökbilimde sık gereken küçük hesaplar için, yalnız Python standart kütüphanesini kullanan, testli ve Türkçe belgelenmiş bir araç kutusu. TÜBİTAK 2209-A ZTF astronomi asistanı çalışmasında karşılaşılan zaman ve koordinat ihtiyaçlarından doğdu.

Kapsam: zaman (JD/MJD, yıldız zamanı), koordinat dönüşümleri, fotometri, gözlem planlama, birimler. Hassasiyet sınırları her işlevin belgesinde yazar; bu kütüphane profesyonel efemeris yazılımının yerine geçmez. Plan: [YOL_HARITASI.md](YOL_HARITASI.md).

```python
from datetime import datetime, timezone
from gokbilim import zaman

jd = zaman.tarihten_jd(datetime(2019, 6, 13, 5, 10, 55, tzinfo=timezone.utc))
print(jd, zaman.jd_den_mjd(jd))

# Yerel yıldız zamanı (derece, doğu boylamı pozitif)
print(zaman.yerel_yildiz_zamani(datetime(1987, 4, 10, 19, 21, tzinfo=timezone.utc), 32.5))
```

Testler: `python -m unittest discover -s tests -v`

Lisans: MIT.

## Saat dilimi örneği

```python
# Gözlem gününün yerel (Istanbul) başlangıcı, UTC olarak
print(zaman.yerel_gun_baslangici(datetime(2024, 6, 15, 21, 30, tzinfo=timezone.utc)))
# 2024-06-15 21:00:00+00:00
```

## Koordinat ve fotometri örneği

```python
from gokbilim import koordinat, fotometri

ra = koordinat.ra_ayristir("18h36m56.336s")      # derece
dec = koordinat.dec_ayristir("+38:47:01.28")
print(koordinat.ekvatordan_galaktige(ra, dec))   # (67.45..., 19.24...) Vega

# Meeus örnek 17.a: Arcturus–Spica
print(koordinat.aci_uzakligi(koordinat.ra_ayristir("14h15m39.7s"), koordinat.dec_ayristir("+19:10:57"),
                             koordinat.ra_ayristir("13h25m11.6s"), koordinat.dec_ayristir("-11:09:41")))  # 32.793

print(fotometri.aki_orani(0, 5))                 # 100.0 (5 büyüklük = 100 kat akı)
print(fotometri.hava_kutlesi(60))                # 1.994 (Kasten–Young)
```

## Gözlem planlama örneği

```python
from datetime import date
from gokbilim import gozlem

# İstanbul'da 7 Kasım 2026: doğuş, tepe, batış (UTC)
dogus, tepe, batis = gozlem.gunes_olaylari(date(2026, 11, 7), 41.01, 28.98)
print(dogus.strftime("%H:%M"), tepe.strftime("%H:%M"), batis.strftime("%H:%M"))  # 04:41 09:47 14:53

# Sivil alacakaranlık (Güneş merkezi -6°)
print(gozlem.gunes_olaylari(date(2026, 11, 7), 41.01, 28.98, gozlem.SIVIL_ALACAKARANLIK))
```

Doğuş/batış zamanları ABD Deniz Gözlemevi (USNO) ile dört yerde karşılaştırıldı; fark en çok 1 dakikadır.

## Komut satırı

```bash
python -m gokbilim jd 2000-01-01T12:00:00Z
python -m gokbilim koordinat 7h45m18.946s +28:01:34.26      # ondalık, galaktik, ekliptik
python -m gokbilim ayrim 14h15m39.7s +19:10:57 13h25m11.6s -11:09:41   # 32.793°
python -m gokbilim gunes --yer 41.01,28.98 --tarih 2026-11-07          # UTC
python -m gokbilim hava-kutlesi 60
```

Geçersiz girdide çıkış kodu 2 ve Türkçe hata iletisi verilir.
