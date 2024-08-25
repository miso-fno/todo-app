from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('パスワード確認', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('登録')

class TodoForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('説明')
    submit = SubmitField('保存')