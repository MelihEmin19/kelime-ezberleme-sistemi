from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from sqlalchemy import inspect

# Constants
DEFAULT_DAILY_WORD_LIMIT = 5
DEFAULT_NOTIFICATION_ENABLED = True

# Uygulama oluşturma
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///word_learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy nesnesi oluşturma
db = SQLAlchemy(app)

# Flask-Login yöneticisi oluşturma
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
login_manager.login_message_category = 'info'

from app import routes, models

def initialize_database():
    """Veritabanını başlatır ve gerekli kolonları ekler"""
    try:
        db.create_all()
        print("Veritabanı şeması güncellendi.")
        
        # User modelinde yeni alanları kontrol et ve ekle
        inspector = inspect(db.engine)
        user_columns = [column['name'] for column in inspector.get_columns('users')]
        
        columns_added = False
        if 'daily_word_limit' not in user_columns:
            db.session.execute(f'ALTER TABLE users ADD COLUMN daily_word_limit INTEGER DEFAULT {DEFAULT_DAILY_WORD_LIMIT}')
            columns_added = True
            
        if 'notification_enabled' not in user_columns:
            db.session.execute(f'ALTER TABLE users ADD COLUMN notification_enabled BOOLEAN DEFAULT {DEFAULT_NOTIFICATION_ENABLED}')
            columns_added = True
            
        if columns_added:
            db.session.commit()
            print("Yeni kolonlar eklendi.")
            
        print("Veritabanı başlatma tamamlandı!")
        
    except Exception as e:
        print(f"Veritabanı başlatma hatası: {e}")
        db.session.rollback()

# Veritabanı şemasını oluştur
with app.app_context():
    initialize_database()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Veritabanı tabloları oluşturuldu!")
    app.run(debug=True, host='0.0.0.0') 