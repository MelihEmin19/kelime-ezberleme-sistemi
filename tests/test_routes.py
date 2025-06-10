import pytest
from app import create_app, db
from app.models import User, Word

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key_for_testing_only'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_home_page(client):
    """Test ana sayfa erişimi"""
    response = client.get('/')
    assert response.status_code == 200

def test_register(client):
    """Test kullanıcı kaydı"""
    test_user_data = {
        'username': 'test_user_123',
        'password': 'SecureTestPass123!',
        'confirm_password': 'SecureTestPass123!'
    }
    response = client.post('/register', data=test_user_data, follow_redirects=True)
    assert response.status_code == 200

def test_login(client):
    """Test kullanıcı girişi"""
    # Önce kullanıcı oluştur
    test_credentials = {
        'username': 'test_user_123',
        'password': 'SecureTestPass123!',
        'confirm_password': 'SecureTestPass123!'
    }
    client.post('/register', data=test_credentials)
    
    # Giriş yap
    login_data = {
        'username': 'test_user_123',
        'password': 'SecureTestPass123!'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200 