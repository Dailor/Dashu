from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired


class AddWork(FlaskForm):
    kw_fields = {"class": "form-control"}
    kw_submit = {"class": "btn btn-primary"}

    work = StringField("Работа", validators=[DataRequired()], render_kw=kw_fields)
    description = TextAreaField("Описание", validators=[DataRequired()], render_kw=kw_fields)
    submit = SubmitField("Отправить", render_kw=kw_submit)


class AppointWork(FlaskForm):
    kw_fields = {"class": "form-control"}
    kw_submit = {"class": "btn btn-primary"}
    kw_selector = {"class": "form-control"}

    worker = SelectField('Выберите работника', validators=[DataRequired()], render_kw=kw_selector)
    work = SelectField("Выберите работу", validators=[DataRequired()], render_kw=kw_selector)
    submit = SubmitField("Отправить", render_kw=kw_submit)


class ResultResponse(FlaskForm):
    kw_fields = {"class": "form-control"}
    kw_submit = {"class": "btn btn-primary"}
    kw_selector = {"class": "form-control"}

    result = TextAreaField("Описание результата", validators=[DataRequired()], render_kw=kw_fields)
    type_result = SelectField("Результат работы", validators=[DataRequired()], render_kw=kw_selector)
    submit = SubmitField("Отправить", render_kw=kw_submit)
