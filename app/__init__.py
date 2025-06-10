from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect
from datetime import datetime

# Constants
DEFAULT_DAILY_WORD_LIMIT = 5
DEFAULT_NOTIFICATION_ENABLED = True

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///word_learning.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
    login_manager.login_message_category = 'info'

    # Template context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Import and register routes and models
    with app.app_context():
        from app import routes, models
        initialize_database()

    return app

def initialize_database():
    """Initialize the database schema and add necessary columns."""
    try:
        db.create_all()
        print("Veritabanı şeması güncellendi.")
        
        # Check and add new columns to the User table
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

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0') 