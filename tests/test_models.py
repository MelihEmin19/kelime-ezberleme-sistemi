import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Word

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='testuser')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user

def test_user_creation(app, test_user):
    """Test kullanıcı oluşturma"""
    with app.app_context():
        assert test_user.username == 'testuser'
        assert test_user.check_password('testpass')

def test_word_creation(app, test_user):
    """Test kelime oluşturma"""
    with app.app_context():
        word = Word(
            english='test',
            turkish='test',
            user_id=test_user.id,
            difficulty='normal',
            next_review=datetime.utcnow()
        )
        db.session.add(word)
        db.session.commit()
        
        assert word.english == 'test'
        assert word.turkish == 'test'
        assert word.user_id == test_user.id
        assert word.difficulty == 'normal'

def test_word_review_update(app, test_user):
    """Test kelime tekrar tarihini güncelleme"""
    with app.app_context():
        word = Word(
            english='test',
            turkish='test',
            user_id=test_user.id,
            difficulty='normal',
            next_review=datetime.utcnow()
        )
        db.session.add(word)
        db.session.commit()
        
        # Bir sonraki tekrar tarihini güncelle
        next_date = datetime.utcnow() + timedelta(days=1)
        word.next_review = next_date
        db.session.commit()
        
        updated_word = Word.query.get(word.id)
        assert (updated_word.next_review - next_date).total_seconds() < 1 