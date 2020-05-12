from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    kw_fields = {"class": "form-control"}
    kw_submit = {"class": "btn btn-primary"}
    kw_selector = {"class": "form-control"}
    kw_photo = {"class": "form-control-file", "accept": "image/*"}

    account_type = SelectField("Тип аккаунта", validators=[DataRequired()], render_kw=kw_selector)

    user_name = StringField("Никнэйм", validators=[DataRequired()], render_kw=kw_fields)
    password = PasswordField("Пароль", validators=[DataRequired()], render_kw=kw_fields)
    password_repeat = PasswordField("Повторите пароль", validators=[DataRequired()], render_kw=kw_fields)

    name = StringField("Имя", validators=[DataRequired()], render_kw=kw_fields)
    surname = StringField("Фамилия", validators=[DataRequired()], render_kw=kw_fields)
    email = StringField("E-mail", validators=[DataRequired()], render_kw=kw_fields)
    birthday = StringField("День рождение", validators=[DataRequired()],
                           render_kw={**kw_fields, "type": "date"})

    photo = FileField("Фото", validators=[DataRequired()], render_kw=kw_photo)
    about_me = TextAreaField("О вас", validators=[DataRequired()], render_kw=kw_fields)

    submit = SubmitField('Отправить', render_kw=kw_submit)


class LoginForm(FlaskForm):
    kw_fields = {"class": "form-control"}
    kw_submit = {"class": "btn btn-primary"}
    kw_checkbox = {'class': "filled-in"}

    email_or_username = StringField("Логин/E-mail", validators=[DataRequired()], render_kw=kw_fields)
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw=kw_fields)
    remember_me = BooleanField("Запомнить меня", render_kw=kw_checkbox)
    submit = SubmitField("Войти", render_kw=kw_submit)
