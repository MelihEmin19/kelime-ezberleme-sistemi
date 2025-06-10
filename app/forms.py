from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifre (Tekrar)', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir kullanıcı adı seçin.')

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class ResetPasswordRequestForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    submit = SubmitField('Şifre Sıfırlama İsteği Gönder')

class WordForm(FlaskForm):
    eng_word_name = StringField('İngilizce Kelime', validators=[DataRequired()])
    tur_word_name = StringField('Türkçe Karşılığı', validators=[DataRequired()])
    picture = FileField('Kelime Görseli (İsteğe Bağlı)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Kelime Ekle')

class WordSampleForm(FlaskForm):
    sample_text = TextAreaField('Örnek Cümle', validators=[DataRequired()])
    submit = SubmitField('Örnek Cümle Ekle')

class SettingsForm(FlaskForm):
    daily_word_limit = IntegerField('Günlük Çalışılacak Kelime Sayısı', 
                                   validators=[DataRequired(), NumberRange(min=1, max=50)],
                                   default=5)
    notification_enabled = BooleanField('Bildirimleri Etkinleştir', default=True)
    submit = SubmitField('Ayarları Kaydet') 