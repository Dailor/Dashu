from flask import Blueprint, render_template, flash, redirect, abort
from flask_login import current_user
from data import db_session
from data.users import Worker, User, Director
from data.work import WorkList
from data.help_models import DirectorInvite, WorkStatus
from modules.forms.WorkForms import ResultResponse
import datetime

blueprint = Blueprint('worker_api', __name__,
                      template_folder='templates')


@blueprint.route("/invites_box")
def invites_box():
    if current_user.is_authenticated is False or current_user.account_type != 3:
        abort(404)
    session = db_session.create_session()
    invites = session.query(DirectorInvite).filter(DirectorInvite.status_invite != 2,
                                                   DirectorInvite.worker_id == current_user.id)

    directors_users = [invite.director.user for invite in invites]
    buttons_a = [('Согласиться', 'agree_invite', 'primary'), ('Отказать', 'access_disagree', 'danger')]
    return render_template('invites_box.html', buttons_a=buttons_a, users=directors_users)


@blueprint.route("/agree_invite/<int:director_id>")
def agree_invite(director_id):
    session = db_session.create_session()
    if current_user.is_authenticated is False or current_user.account_type != 3 or session.query(Director).get(
            director_id) is None:
        abort(404)
    invite_from_director = session.query(DirectorInvite).filter(DirectorInvite.director_id == director_id,
                                                                DirectorInvite.worker_id == current_user.id,
                                                                DirectorInvite.status_invite == 1).first()
    if invite_from_director is None:
        abort(404)

    worker = session.query(Worker).get(invite_from_director.worker_id)
    worker.director_id = invite_from_director.director_id

    session.delete(invite_from_director)
    session.merge(worker)
    session.commit()
    status = f"Теперь ваш начальник {session.query(Director).get(director_id).user.get_full_name()}"
    msg_type = "success"
    flash(status, msg_type)
    return redirect('/invites_box')


@blueprint.route('/works')
def works_load():
    if current_user.is_authenticated is False or current_user.account_type != 3:
        abort(404)

    session = db_session.create_session()

    worker = session.query(Worker).get(current_user.id)

    director_is = session.query(Worker).get(current_user.id).director_id

    table_data = list()
    for worklist in session.query(WorkList).filter(WorkList.worker_id == current_user.id, WorkList.status == 2):
        temp = list()
        temp.append(worklist.work_url.work)
        temp.append(worklist.work_url.description)
        temp.append(worklist.id)
        table_data.append(temp)

    return render_template('works.html', director_is=director_is, table_data=table_data)


@blueprint.route('/access_disagree/<int:director_id>')
def disagree_invite(director_id):
    session = db_session.create_session()
    if current_user.is_authenticated is False or current_user.account_type != 3 or session.query(Director).get(
            director_id) is None:
        abort(404)

    invite_from_director = session.query(DirectorInvite).filter(DirectorInvite.director_id == director_id,
                                                                DirectorInvite.worker_id == current_user.id,
                                                                DirectorInvite.status_invite == 1).first()
    if invite_from_director is None:
        abort(404)

    invite_from_director.status_invite = 2

    session.merge(invite_from_director)
    session.commit()

    status = f"Ваша заявка директору {session.query(Director).get(director_id).user.get_full_name()}"
    msg_type = "success"
    flash(status, msg_type)
    return redirect('/invites_box')


@blueprint.route("/make_work/<int:work_list_id>", methods=["POST", "GET"])
def make_work(work_list_id):
    if current_user.is_authenticated is False or current_user.account_type != 3:
        abort(404)

    session = db_session.create_session()
    worklist = session.query(WorkList).get(work_list_id)

    if worklist.worker_id != current_user.id or worklist.status != 2:
        abort(404)

    form = ResultResponse()
    if form.is_submitted():
        worklist.status = form.data["type_result"]
        worklist.work_result_message = form.data["result"]
        worklist.work_end = datetime.datetime.now()
        session.merge(worklist)
        session.commit()
        return redirect('/works')

    form.type_result.choices = ((1, "Выполнено"), (3, "Не выполнено"))

    return render_template('register.html', action_title="Результат работы", form=form,
                           container_name='add_work_container')
