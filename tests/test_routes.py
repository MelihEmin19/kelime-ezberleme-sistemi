import pytest
from app import create_app, db
from app.models import User, Word

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
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
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass',
        'confirm_password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Hesap oluşturuldu' in response.data

def test_login(client):
    """Test kullanıcı girişi"""
    # Önce kullanıcı oluştur
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    
    # Giriş yap
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Giriş başarılı' in response.data 