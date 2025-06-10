from app import app, db
from app.models import User, Word, WordSample, StudySession

if __name__ == "__main__":
    with app.app_context():
        # Veritabanı tablolarını oluştur
        db.create_all()
        print("Veritabanı şeması güncellendi.")
        
        # Son kullanıcı kelime sayısını kontrol et
        try:
            user = User.query.filter_by(username='admin').first()
            if user:
                word_count = Word.query.filter_by(user_id=user.id).count()
                print(f"Admin kullanıcısının kelime sayısı: {word_count}")
        except Exception as e:
            print(f"Kelime sayısı kontrol edilirken hata oluştu: {str(e)}")
    
    # Uygulamayı çalıştır    
    app.run(debug=True, host='0.0.0.0') 