# Kelime Ezberleme Sistemi

Bu proje, kullanıcıların yabancı dil kelime öğrenmesini kolaylaştırmak için geliştirilmiş bir web uygulamasıdır.

## Özellikler

- Kullanıcı kaydı ve giriş sistemi
- Kelime ekleme ve düzenleme
- Örnek cümle ekleyebilme
- 6 Seferli Öğrenme Algoritması (1 gün, 1 hafta, 1 ay, 3 ay, 6 ay, 1 yıl tekrar aralıkları)
- Detaylı istatistik ve analiz raporları
- Öğrenme ilerleme grafikleri
- Çalışma modları
- Wordle kelime oyunu

## Teknolojiler

- Python
- Flask
- SQLite
- HTML/CSS/Bootstrap
- JavaScript

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
flask db upgrade
```
5. Uygulamayı çalıştırın:
```
python run.py
```

## Kullanım

### Kullanıcı Kaydı ve Giriş

- Ana sayfadaki "Kayıt Ol" bağlantısını kullanarak yeni bir hesap oluşturun
- Kullanıcı adı ve şifrenizle giriş yapın

### Kelime Ekleme

- "Kelime Ekle" sayfasında İngilizce-Türkçe kelime çiftlerini ekleyin
- Her kelime için örnek cümleler ekleyerek öğrenmeyi kolaylaştırın
- Kelimenin zorluk derecesini belirleyin

### Kelime Çalışma

- "Çalış" sayfasında günlük kelime çalışma rutininizi gerçekleştirin
- 6 Seferli Algoritma ile kelimeleri belirli aralıklarla tekrar edin
- Wordle oyunu ile öğrenmeyi eğlenceli hale getirin

### İstatistikler

- "İstatistikler" sayfasında ilerlemenizi takip edin
- Öğrendiğiniz kelime sayısı ve başarı oranınızı görüntüleyin
- Zorluk seviyelerine göre kelime dağılımını inceleyin

## İletişim

Proje Sahibi: [MelihEmin19](https://github.com/MelihEmin19) 
