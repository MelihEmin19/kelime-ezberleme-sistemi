from flask import render_template, url_for, flash, redirect, request, jsonify, current_app
from . import db
from .forms import (RegistrationForm, LoginForm, ResetPasswordRequestForm,
                      WordForm, WordSampleForm, SettingsForm)
from .models import User, Word, WordSample, StudySession
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
import os
import secrets
import random
import hashlib
from sqlalchemy.sql import func

# Constants - Magic numbers'ları constants'a çevirdim
LEARNING_COMPLETE_COUNT = 6
REVIEW_INTERVALS = [1, 7, 30, 90, 180, 365]  # days
WORDLE_WORD_LENGTH = 5
DEFAULT_OPTIONS = ["kelime", "çeviri", "anlam", "gramer", "fiil", "isim"]

# Helper functions - Code smells düzeltmesi: Extract Method
def get_today_boundaries():
    """Bugünün başlangıç ve bitiş zamanlarını döndürür"""
    today = datetime.utcnow()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    return today_start, today_end

def create_word_options(word, user_id):
    """Kelime için çoktan seçmeli seçenekler oluşturur"""
    correct_answer = word.tur_word_name
    options = [correct_answer]
    
    # Yanlış seçenekler - admin'in kelimelerini de dahil et
    wrong_words = Word.query.filter(
        Word.id != word.id,
        ((Word.user_id == user_id) | (Word.user_id == 1)),
        Word.tur_word_name != "",
        Word.tur_word_name != correct_answer
    ).limit(10).all()
    
    wrong_options = [w.tur_word_name for w in wrong_words][:3]
    
    # Yeterli seçenek yoksa varsayılan ekle
    if len(wrong_options) < 3:
        needed = 3 - len(wrong_options)
        available_defaults = [opt for opt in DEFAULT_OPTIONS if opt not in options]
        wrong_options.extend(available_defaults[:needed])
    
    options.extend(wrong_options[:3])
    random.shuffle(options)
    return options

def get_due_sessions(user_id, today_end):
    """Bugün tekrar edilmesi gereken oturumları döndürür"""
    return StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.next_review_date <= today_end,
        StudySession.completed == False
    ).order_by(StudySession.next_review_date).all()

def create_new_study_sessions(user_id, available_slots, today_start):
    """Yeni kelimeler için çalışma oturumları oluşturur"""
    if available_slots <= 0:
        return
        
    studied_word_ids = [s.word_id for s in StudySession.query.filter_by(user_id=user_id).all()]
    
    # Admin'in kelimelerini de dahil et
    new_words = Word.query.filter(
        ((Word.user_id == user_id) | (Word.user_id == 1)),
        ~Word.id.in_(studied_word_ids)
    ).order_by(Word.created_at).limit(available_slots).all()
    
    for word in new_words:
        session = StudySession(
            word_id=word.id,
            user_id=user_id,
            next_review_date=today_start
        )
        db.session.add(session)
    db.session.commit()

def calculate_next_review_date(correct_count):
    """Sonraki tekrar tarihini hesaplar"""
    if correct_count >= LEARNING_COMPLETE_COUNT:
        return None
    
    interval_days = REVIEW_INTERVALS[correct_count - 1]
    next_date = datetime.utcnow() + timedelta(days=interval_days)
    return next_date.replace(hour=0, minute=0, second=0, microsecond=0)

def get_daily_target_word(user_id):
    """Wordle için günün kelimesini belirler"""
    # Admin'in kelimelerini de dahil et
    five_letter_words = Word.query.filter(
        ((Word.user_id == user_id) | (Word.user_id == 1)),
        func.length(Word.eng_word_name) == WORDLE_WORD_LENGTH
    ).all()
    
    if not five_letter_words:
        return None, None
    
    today = datetime.now().strftime('%Y-%m-%d')
    hash_object = hashlib.md5(today.encode())
    word_index = int(hash_object.hexdigest(), 16) % len(five_letter_words)
    return five_letter_words[word_index].eng_word_name.upper(), five_letter_words[word_index]

def calculate_wordle_result(guess, target_word):
    """Wordle tahmin sonucunu hesaplar"""
    result = []
    target_letters = list(target_word)
    guess_letters = list(guess)
    
    # Yeşilleri işaretle
    for i in range(WORDLE_WORD_LENGTH):
        if guess_letters[i] == target_letters[i]:
            result.append('correct')
            target_letters[i] = None
            guess_letters[i] = None
        else:
            result.append(None)
    
    # Sarıları işaretle
    for i in range(WORDLE_WORD_LENGTH):
        if result[i] is None:
            if guess_letters[i] in target_letters:
                result[i] = 'present'
                target_letters[target_letters.index(guess_letters[i])] = None
            else:
                result[i] = 'absent'
    
    return result

@current_app.route('/')
@current_app.route('/index')
def index():
    return render_template('index.html', title='Ana Sayfa')

@current_app.route('/exam_module')
def exam_module():
    algorithm_steps = [
        {
            'title': 'Temel 6 Sefer Quiz Algoritması',
            'description': f'Bir kelimeyi tam öğrenmek için {LEARNING_COMPLETE_COUNT} kez doğru bilmeniz gerekir. Yanlış cevap verirseniz süreç başa döner.'
        },
        {
            'title': 'Tekrarlama Aralıkları',
            'description': 'Kelimelerin tekrarı belirlenen aralıklara göre yapılır: 1 gün, 1 hafta, 1 ay, 3 ay, 6 ay, 1 yıl.'
        }
    ]
    
    exam_rules = [
        f'Her kelimeyi tam öğrenmek için {LEARNING_COMPLETE_COUNT} kez doğru bilmeniz gerekir.',
        'Yanlış cevap verirseniz, o kelime için süreç başa döner.',
        'Kelimelerin tekrarı belirlenen aralıklara göre yapılır.',
        'Her gün ayarlarınızda belirlediğiniz sayıda kelime çalışılır (varsayılan: 5).',
        f'Bir kelimeyi {LEARNING_COMPLETE_COUNT} kez doğru bildiğinizde, kelime öğrenilmiş kabul edilir.'
    ]
    
    return render_template('exam_module.html', 
                          title='Sınav Modülü', 
                          algorithm_steps=algorithm_steps, 
                          exam_rules=exam_rules)

@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Hesabınız başarıyla oluşturuldu!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Kayıt Ol', form=form)

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Giriş başarısız. Lütfen kullanıcı adı ve şifrenizi kontrol edin.', 'danger')
    
    return render_template('login.html', title='Giriş Yap', form=form)

@current_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@current_app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Şifre sıfırlama talimatları için e-posta adresinizi kontrol edin.', 'info')
            return redirect(url_for('login'))
        flash('Bu kullanıcı adıyla kayıtlı bir hesap bulunamadı.', 'warning')
    
    return render_template('reset_password_request.html', title='Şifre Sıfırlama', form=form)

@current_app.route('/words')
@login_required
def words():
    # Admin'in kelimelerini de göster (ID: 1)
    user_words = Word.query.filter(
        (Word.user_id == current_user.id) | (Word.user_id == 1)
    ).all()
    return render_template('words.html', title='Kelimelerim', words=user_words)

@current_app.route('/add_word', methods=['GET', 'POST'])
@login_required
def add_word():
    form = WordForm()
    if form.validate_on_submit():
        picture_file = None
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
                
        word = Word(
            eng_word_name=form.eng_word_name.data,
            tur_word_name=form.tur_word_name.data,
            picture=picture_file,
            user_id=current_user.id
        )
        
        db.session.add(word)
        db.session.commit()
        flash('Kelime başarıyla eklendi!', 'success')
        return redirect(url_for('words'))
    
    return render_template('add_word.html', title='Kelime Ekle', form=form)

def save_picture(form_picture):
    """Yüklenen resmi kaydeder ve dosya adını döndürür"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/word_pics', picture_fn)
    
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    form_picture.save(picture_path)
    return picture_fn

@current_app.route('/word/<int:word_id>', methods=['GET', 'POST'])
@login_required
def word_detail(word_id):
    word = Word.query.get_or_404(word_id)
    # Admin'in kelimelerine de erişim izni ver
    if word.user_id != current_user.id and word.user_id != 1:
        flash('Bu kelimeyi görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('words'))
    
    form = WordSampleForm()
    if form.validate_on_submit():
        sample = WordSample(
            word_id=word.id,
            sample_text=form.sample_text.data
        )
        db.session.add(sample)
        db.session.commit()
        flash('Örnek cümle başarıyla eklendi!', 'success')
        return redirect(url_for('word_detail', word_id=word.id))
    
    return render_template('word_detail.html', title=word.eng_word_name, word=word, form=form)

@current_app.route('/study')
@login_required
def study():
    today_start, today_end = get_today_boundaries()
    daily_limit = current_user.daily_word_limit
    
    # Bugün tekrar edilecek kelimeler
    due_sessions = get_due_sessions(current_user.id, today_end)
    
    # Yeni kelimeler için yer var mı?
    available_slots = max(0, daily_limit - len(due_sessions))
    create_new_study_sessions(current_user.id, available_slots, today_start)
    
    # Bugün çalışılacak kelimeleri getir
    today_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.next_review_date <= today_end,
        StudySession.completed == False
    ).order_by(StudySession.correct_count, StudySession.next_review_date).limit(daily_limit).all()
    
    # Kelimeler için seçenekler hazırla
    today_words = []
    for session in today_sessions:
        word = Word.query.get(session.word_id)
        options = create_word_options(word, current_user.id)
        
        today_words.append({
            'word': word,
            'session': session,
            'options': options
        })
    
    return render_template('study.html', title='Kelime Çalışma', word_sessions=today_words)

@current_app.route('/check_answer/<int:session_id>', methods=['POST'])
@login_required
def check_answer(session_id):
    session = StudySession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('Bu çalışma oturumuna erişim yetkiniz yok.', 'danger')
        return redirect(url_for('study'))
    
    word = Word.query.get(session.word_id)
    user_answer = request.form.get('answer', '').strip()
    is_correct = user_answer == word.tur_word_name
    
    session.attempt_count += 1
    session.last_studied = datetime.utcnow()
    
    if is_correct:
        session.correct_count += 1
        
        if session.correct_count >= LEARNING_COMPLETE_COUNT:
            session.completed = True
            flash(f'Tebrikler! "{word.eng_word_name}" kelimesini öğrendiniz!', 'success')
        else:
            next_review_date = calculate_next_review_date(session.correct_count)
            session.next_review_date = next_review_date
            interval_days = REVIEW_INTERVALS[session.correct_count - 1]
            flash(f'Doğru! {interval_days} gün sonra tekrar çalışacaksınız.', 'success')
    else:
        flash(f'Yanlış. Doğru cevap: {word.tur_word_name}', 'danger')
        session.correct_count = 0
        session.next_review_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    db.session.commit()
    return redirect(url_for('study'))

@current_app.route('/statistics')
@login_required
def statistics():
    # Admin'in kelimelerini de dahil et
    user_words = Word.query.filter(
        (Word.user_id == current_user.id) | (Word.user_id == 1)
    ).count()
    
    learned_sessions = StudySession.query.filter_by(
        user_id=current_user.id, 
        completed=True
    ).count()
    
    in_progress = StudySession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).count()
    
    success_rate = (learned_sessions / user_words * 100) if user_words > 0 else 0
    
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_learned = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.completed == True,
        StudySession.last_studied >= one_week_ago
    ).count()
    
    return render_template(
        'statistics.html', 
        title='İstatistikler',
        total_words=user_words,
        learned_words=learned_sessions,
        in_progress=in_progress,
        success_rate=success_rate,
        recent_learned=recent_learned
    )

@current_app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    
    if request.method == 'GET':
        form.daily_word_limit.data = current_user.daily_word_limit
        form.notification_enabled.data = current_user.notification_enabled
    
    if form.validate_on_submit():
        current_user.daily_word_limit = form.daily_word_limit.data
        current_user.notification_enabled = form.notification_enabled.data
        db.session.commit()
        flash('Ayarlarınız güncellendi!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', title='Ayarlar', form=form)

@current_app.route('/wordle')
@login_required
def wordle():
    return render_template('wordle.html', title='Wordle Oyunu')

@current_app.route('/wordle_guess', methods=['POST'])
@login_required
def wordle_guess():
    data = request.get_json()
    guess = data.get('guess', '').upper()
    
    if len(guess) != WORDLE_WORD_LENGTH:
        return jsonify({'error': f'Kelime {WORDLE_WORD_LENGTH} harfli olmalı'})
    
    # Günün kelimesini al
    target_word, target_word_obj = get_daily_target_word(current_user.id)
    if not target_word:
        return jsonify({'error': 'Yeterli kelime bulunamadı'})
    
    # Kelime kontrolü - admin'in kelimelerini de dahil et
    word_exists = Word.query.filter(
        ((Word.user_id == current_user.id) | (Word.user_id == 1)),
        func.upper(Word.eng_word_name) == guess
    ).first()
    
    if not word_exists:
        return jsonify({'error': 'Geçersiz kelime'})
    
    # Sonucu hesapla
    result = calculate_wordle_result(guess, target_word)
    game_won = all(r == 'correct' for r in result)
    
    return jsonify({
        'result': result,
        'target': target_word,
        'won': game_won,
        'turkish': target_word_obj.tur_word_name
    }) 