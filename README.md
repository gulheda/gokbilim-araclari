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
