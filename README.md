# Kelime Ezberleme Sistemi

Flask ile geliştirilmiş bir kelime ezberleme ve hatırlama sistemi.

## Özellikler

- Kullanıcı kaydı ve giriş sistemi
- Kelime ekleme ve düzenleme
- Örnek cümle ekleyebilme
- 6 Seferli Öğrenme Algoritması (1 gün, 1 hafta, 1 ay, 3 ay, 6 ay, 1 yıl tekrar aralıkları)
- Kelime zorluk derecelendirme (kolay/normal/zor)
- Detaylı istatistik ve analiz raporları
- Öğrenme ilerleme grafikleri

## Kurulum

1. Python 3.7 veya daha yeni bir sürüm gereklidir.
2. Sanal ortam oluşturun ve aktifleştirin:
```
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```
3. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```
4. Veritabanını oluşturun:
```
python recreate_db.py
```
5. Uygulamayı çalıştırın:
```
python run.py
```

## Veritabanı Şema Güncelleme Kılavuzu

Eğer "sqlalchemy.exc.OperationalError: no such column: words.difficulty" hatası alıyorsanız, veritabanı şemanız güncel değil demektir. Şemayı güncellemek için aşağıdaki adımları izleyin:

### 1. Yöntem: Veritabanını Sıfırdan Oluşturma (VERİLER KAYBOLUR)

Bu yöntem veritabanını tamamen sıfırlar, tüm verileriniz silinir.

```
python recreate_db.py
```

### 2. Yöntem: Şemayı Güncelleme (VERİLER KORUNUR)

Bu yöntem sadece eksik sütunları ekler, veriler korunur.

```
python simple_update.py
```

### 3. Elle Çözüm (Veritabanı Hatası Devam Ederse)

1. SQLite tarayıcısı veya başka bir veritabanı yönetim aracıyla `instance/word_learning.db` dosyasını açın
2. Aşağıdaki SQL komutunu çalıştırın:
```sql
ALTER TABLE words ADD COLUMN difficulty VARCHAR(20) DEFAULT 'normal';
```

## En Son Değişiklikler

- Zorluk derecesi (difficulty) sütunu eklendi
- İstatistik sayfasında zorluk dağılımı grafiği eklendi
- Hata yakalama mekanizmaları geliştirildi
- Veritabanı şema güncelleme yetenekleri eklendi

## Kullanım

### Kullanıcı Kaydı ve Giriş

- Ana sayfadaki "Kayıt Ol" bağlantısını kullanarak yeni bir hesap oluşturun
- Kullanıcı adı ve şifrenizle giriş yapın

### Kelime Ekleme

- "Kelime Ekle" sayfasında İngilizce-Türkçe kelime çiftlerini ve isteğe bağlı resimleri ekleyin
- Her kelime için örnek cümleler ekleyerek öğrenmeyi kolaylaştırın

### Kelime Çalışma

- "Çalış" sayfasında günlük kelime çalışma rutininizi gerçekleştirin
- 6 Seferli Algoritma, öğrendiğiniz kelimeleri doğru aralıklarla tekrar etmenizi sağlar
- Her kelimeyi 6 kez doğru bildiğinizde, bu kelime "öğrenilmiş" olarak işaretlenir

### İstatistikler

- "İstatistikler" sayfasında ilerlemenizi takip edin
- Öğrendiğiniz kelime sayısı, öğrenme aşamasındaki kelimeler ve başarı oranınızı görüntüleyin

## Katkıda Bulunma

1. Bu repoyu forklayın
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inize push yapın (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje Sahipleri: [GitHub Kullanıcı Adı](https://github.com/kullanici-adi) 