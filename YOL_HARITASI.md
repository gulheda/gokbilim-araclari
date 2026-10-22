# Yol haritası

Her gün bu listeden bir sonraki **işaretlenmemiş** madde seçilir, testiyle birlikte eklenir. Yeni fikirler listenin sonuna eklenir. Kurallar: yalnız standart kütüphane, her işlev için test, formüllerin kaynağı veya bilinen referans değeri docstring'de, sonuçlar yaklaşık ise hassasiyet belirtilir.

## Zaman
- [x] JD ↔ UTC, MJD, J2000'den beri gün
- [ ] Greenwich ortalama yıldız zamanı (GMST)
- [ ] Yerel yıldız zamanı (boylama göre)
- [ ] Gün başlangıcı ve saat dilimi yardımcıları (Europe/Istanbul örnekleri)
- [ ] Ay takvimi: yeni ay / dolunay yaklaşık zamanları

## Koordinatlar
- [ ] Derece ↔ saat/dakika/saniye (RA) ve derece/yay dakikası/yay saniyesi (Dec) biçimleri
- [ ] RA/Dec biçim ayrıştırıcı ("12h30m45s", "+45:30:15")
- [ ] İki nokta arası açısal uzaklık (haversine ve vektör sürümü)
- [ ] Ekvator ↔ galaktik dönüşümü (J2000)
- [ ] Ekvator ↔ ufuk koordinatları (yükseklik, azimut)
- [ ] Ekvator ↔ ekliptik dönüşümü

## Fotometri
- [ ] Büyüklük ↔ akı oranı
- [ ] Mutlak büyüklük ve uzaklık modülü
- [ ] Hava kütlesi (plane-parallel ve Kasten–Young)
- [ ] Renk indeksleri ve bant adları (ZTF g/r/i örnekleri)
- [ ] Büyüklük hatası yayılımı

## Gözlem planlama
- [ ] Güneş'in yaklaşık konumu
- [ ] Gün doğumu, batımı ve alacakaranlık saatleri
- [ ] Bir hedefin gece boyunca yüksekliği
- [ ] Ay'ın yaklaşık konumu ve evresi
- [ ] Hedef–Ay uzaklığı uyarısı

## Fizik ve birimler
- [ ] Astronomik birim dönüşümleri (AU, pc, ışık yılı, güneş yarıçapı/kütlesi)
- [ ] Kepler üçüncü yasası
- [ ] Hubble yasası ve kırmızıya kayma → hız (göreli olmayan ve göreli)
- [ ] Siyah cisim ışıması ve Wien yasası
- [ ] Yörünge dönemi ve kaçış hızı

## Araçlar
- [ ] Komut satırı arayüzü (`python -m gokbilim ...`)
- [ ] Türkçe hata iletileri ve birim etiketleri için tek yardımcı modül
- [ ] Örnek defter: ZTF uyarısı gözlem zamanı ve koordinat okuma
- [ ] Sürüm etiketi ve paket yayını için `pyproject.toml` temizliği
