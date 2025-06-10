import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Word

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key_for_testing_only'
    return app

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='test_user_model')
        # Test için güvenli şifre kullanımı
        secure_test_pass = 'TestSecurePass456!'
        user.set_password(secure_test_pass)
        db.session.add(user)
        db.session.commit()
        return user

def test_user_creation(app, test_user):
    """Test kullanıcı oluşturma"""
    with app.app_context():
        assert test_user.username == 'test_user_model'
        # Güvenli test şifresi kontrolü
        assert test_user.check_password('TestSecurePass456!')

def test_word_creation(app, test_user):
    """Test kelime oluşturma"""
    with app.app_context():
        word = Word(
            eng_word_name='test_word',
            tur_word_name='test_kelime',
            user_id=test_user.id,
            created_at=datetime.utcnow()
        )
        db.session.add(word)
        db.session.commit()
        
        assert word.eng_word_name == 'test_word'
        assert word.tur_word_name == 'test_kelime'
        assert word.user_id == test_user.id

def test_word_review_update(app, test_user):
    """Test kelime tekrar tarihini güncelleme"""
    with app.app_context():
        word = Word(
            eng_word_name='test_word',
            tur_word_name='test_kelime',
            user_id=test_user.id,
            created_at=datetime.utcnow()
        )
        db.session.add(word)
        db.session.commit()
        
        # Test için güncellenmiş tarih
        updated_date = datetime.utcnow() + timedelta(days=1)
        word.created_at = updated_date
        db.session.commit()
        
        updated_word = Word.query.get(word.id)
        assert (updated_word.created_at - updated_date).total_seconds() < 1 