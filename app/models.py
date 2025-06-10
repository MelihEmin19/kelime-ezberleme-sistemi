from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    daily_word_limit = db.Column(db.Integer, default=5)  # Günlük çalışılacak yeni kelime sayısı
    notification_enabled = db.Column(db.Boolean, default=True)  # Bildirim tercihi
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Word(db.Model):
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    eng_word_name = db.Column(db.String(255), nullable=False)
    tur_word_name = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    samples = db.relationship('WordSample', backref='word', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Word {self.eng_word_name}>'

class WordSample(db.Model):
    __tablename__ = 'word_samples'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    sample_text = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<WordSample for Word ID: {self.word_id}>'

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attempt_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    next_review_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    last_studied = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudySession for Word ID: {self.word_id}, User ID: {self.user_id}>' 