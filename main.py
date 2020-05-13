import datetime
from flask_socketio import SocketIO
from flask import Flask, render_template, redirect, request, url_for, flash, session, Response, abort
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from data import db_session
from data.users import User, Director, Worker
from data.help_models import AccountType, WorkerStatus, WorkStatus, InviteStatus
from modules.forms.AuthForms import RegisterForm, LoginForm
from modules.handlers import for_director, for_worker
from flask_restful import reqparse, abort, Api, Resource
from modules.api import UserAPI, WorksListAPI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return render_template('erorr_page.html', title="Не найдено"), 404


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    acc_type = current_user.account_type
    if acc_type == 2:
        return redirect('/company')
    elif acc_type == 3:
        return redirect('/works')
    return render_template('index.html', titile='Главная')


def check_user_data_in_db(email, username):
    msg = "Пользователь с таким {} уже существует"
    session = db_session.create_session()
    if session.query(User).filter(User.email == email).first():
        return msg.format("email")

    elif session.query(User).filter(User.user_name == username).first():
        return msg.format("ником")
    return None


def user_registration(form):
    """

    :param form:
    :return: msg_type, status
    """
    # alert - success
    # alert - warning
    # alert - danger

    msg_type = None
    status = None

    if form.password.data != form.password_repeat.data:
        return 'danger', 'Пароли не совпадают'
    check_data = check_user_data_in_db(form.email.data, form.user_name.data)

    if check_data is not None:
        return 'danger', check_data

    if form.email.data.rfind('@') > form.email.data.rfind('.'):
        return 'danger', "Формат почты exm@ex.ex"

    if form.user_name.data.find('@') != -1:
        return 'danger', "Ник не может содержать '@' символы"

    user = User()

    user.account_type = int(form.data['account_type'])
    user.user_name = form.user_name.data
    user.set_password(form.password.data)
    user.surname = form.surname.data
    user.name = form.name.data
    user.birthday = datetime.datetime.strptime(form.birthday.data, '%Y-%m-%d')
    user.photo = form.data['photo'].read()
    user.email = form.email.data
    user.about_me = form.about_me.data

    session = db_session.create_session()
    session.add(user)
    session.commit()

    if int(form.data['account_type']) == 2:
        director = Director()
        director.director_id = user.id
        session.add(director)
    elif int(form.data["account_type"]) == 3:
        worker = Worker()
        worker.worker_id = user.id
        session.add(worker)

    session.commit()
    return 'success', "Аккаунт успешно зарегистрирован "


@app.route('/register', methods=["GET", "POST"])
def register():
    session = db_session.create_session()
    form = RegisterForm()
    form.account_type.choices = [(m.id, m.name) for m in session.query(AccountType).all() if m.id != 1]
    try:
        form.account_type.render_kw['disabled'] = 'disabled'
        form.password.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}
        form.password_repeat.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}
        form.photo.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}

        form.account_type.render_kw.pop('disabled')

        form.password.render_kw.pop('disabled')
        form.password.render_kw.pop('hidden')

        form.password_repeat.render_kw.pop('disabled')
        form.password_repeat.render_kw.pop('hidden')

        form.photo.render_kw.pop('disabled')
        form.photo.render_kw.pop('hidden')
    except:
        pass
    if form.is_submitted():
        msg_type, status = user_registration(form)
        flash(status, msg_type)
        if msg_type == 'success':
            return redirect(url_for('login'))

    return render_template('register.html', title="Регистрация", action_title="Регистрация", form=form)


@app.route('/settings', methods=["POST", "GET"])
@login_required
def settings_user():
    form = RegisterForm()

    session = db_session.create_session()

    form.account_type.render_kw['disabled'] = 'disabled'
    form.password.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}
    form.password_repeat.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}
    form.photo.render_kw = {**form.about_me.render_kw, 'disabled': 'disabled', 'hidden': 'hidden'}

    form.account_type.choices = [
        [current_user.account_type, session.query(AccountType).get(current_user.account_type).name]]

    if form.is_submitted() is False:
        form.user_name.data = current_user.user_name
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.birthday.data = str(current_user.birthday).split()[0]
        form.about_me.data = current_user.about_me

    if form.is_submitted():
        current_user.user_name = form.user_name.data
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        current_user.birthday = datetime.datetime.strptime(form.birthday.data, '%Y-%m-%d')
        current_user.about_me = form.about_me.data

        session.merge(current_user)
        session.commit()
    return render_template('register.html', action_title="Редактирование", form=form)


def check_on_auth(form):
    email_or_username = form.email_or_username.data
    password = form.password.data

    session = db_session.create_session()

    for user in session.query(User).filter(((User.email == email_or_username) | (User.user_name == email_or_username))):
        if user.check_password(password):
            return user

    return None


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.is_submitted():
        user = check_on_auth(form)
        if user:
            login_user(user, remember=form.remember_me.data)
            session["username"] = user.name
            return redirect('/')
        else:
            flash("Не верные данные", 'danger')
    return render_template('login.html', form=form)


def add_help_types():
    ACCOUNT_TYPES = [("Админ", '/register/admin'),
                     ("Директор", '/register/director'),
                     ("Работник", '/register/worker')]
    WORKERS_STATUS = ["Свободен", "Занят"]
    WORK_STATUS = ["Выполнена", "Выполняется", "Отклонена"]
    INVITE_STATUS = ["В ожидании", "Отказано"]

    models = {
        WorkerStatus: WORKERS_STATUS,
        WorkStatus: WORK_STATUS,
        InviteStatus: INVITE_STATUS

    }

    session = db_session.create_session()
    for model, list_data in models.items():
        for data in list_data:
            ex_model = model()
            ex_model.name = data
            session.add(ex_model)

    for name, url in ACCOUNT_TYPES:
        ex = AccountType()
        ex.name = name
        # ex.url_path = url
        session.add(ex)

    session.commit()


@app.route('/image/<int:id>')
def get_image(id):
    session = db_session.create_session()
    user = session.query(User).get(id)
    if user is None:
        return abort(404)
    return Response(user.photo, mimetype='image/jpeg')


def add_some_data():
    # add_help_types()
    pass


def main():
    db_session.global_init('db/database.sqlite')
    add_some_data()

    app.register_blueprint(for_director.blueprint)
    app.register_blueprint(for_worker.blueprint)

    api.add_resource(WorksListAPI.WorkListAPI, '/api/works_list')
    api.add_resource(UserAPI.UsersList, '/api/users')

    app.run()


if __name__ == '__main__':
    main()
