#!/usr/bin/env python3
"""
Veritabanı şemasını düzeltmek için script
"""

from app import create_app, db
from app.models import User, Word, WordSample, StudySession
from sqlalchemy import inspect, text

def fix_database():
    app = create_app()
    
    with app.app_context():
        print("Veritabanı şeması kontrol ediliyor...")
        
        # Veritabanı tablolarını oluştur
        db.create_all()
        print("✓ Tablolar oluşturuldu/kontrol edildi")
        
        # Word tablosundaki sütunları kontrol et
        inspector = inspect(db.engine)
        word_columns = [col['name'] for col in inspector.get_columns('words')]
        
        print(f"Word tablosundaki sütunlar: {word_columns}")
        
        # Eğer eski sütun isimleri varsa düzelt
        if 'english' in word_columns and 'eng_word_name' not in word_columns:
            print("Eski sütun isimleri tespit edildi, güncelleniyor...")
            try:
                # Eski veriler için yeni tablo oluştur
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS words_new (
                        id INTEGER PRIMARY KEY,
                        eng_word_name VARCHAR(255) NOT NULL,
                        tur_word_name VARCHAR(255) NOT NULL,
                        picture VARCHAR(255),
                        user_id INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """))
                
                # Eski verilerden yeni tabloya kopyala
                db.session.execute(text("""
                    INSERT INTO words_new (id, eng_word_name, tur_word_name, picture, user_id, created_at)
                    SELECT id, english, turkish, picture, user_id, created_at 
                    FROM words
                """))
                
                # Eski tabloyu sil ve yeni tabloyu yeniden adlandır
                db.session.execute(text("DROP TABLE words"))
                db.session.execute(text("ALTER TABLE words_new RENAME TO words"))
                
                db.session.commit()
                print("✓ Sütun isimleri güncellendi")
                
            except Exception as e:
                print(f"Sütun güncelleme hatası: {e}")
                db.session.rollback()
        
        # User tablosundaki eksik sütunları ekle
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'daily_word_limit' not in user_columns:
            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN daily_word_limit INTEGER DEFAULT 5"))
                print("✓ daily_word_limit sütunu eklendi")
            except Exception as e:
                print(f"daily_word_limit sütunu eklenirken hata: {e}")
        
        if 'notification_enabled' not in user_columns:
            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN notification_enabled BOOLEAN DEFAULT 1"))
                print("✓ notification_enabled sütunu eklendi")
            except Exception as e:
                print(f"notification_enabled sütunu eklenirken hata: {e}")
        
        db.session.commit()
        print("✓ Veritabanı şeması başarıyla güncellendi!")

if __name__ == "__main__":
    fix_database() 