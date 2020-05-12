from flask import Blueprint, render_template, flash, redirect, abort
from flask_login import current_user
from data import db_session
from data.users import Worker, Director
from data.work import Work, WorkList
from data.help_models import DirectorInvite, WorkStatus
from modules.forms.WorkForms import AddWork, AppointWork

blueprint = Blueprint('director_api', __name__,
                      template_folder='templates')


@blueprint.route('/company')
def company_load():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    table_data = list()
    session = db_session.create_session()

    a_buttons_not_ready = [('Изменить', "change_appoint_work"), ("Удалить", "delte_appoint_work")]
    a_buttons_ready = [('Посмотореть результат', "get_result_appoint_work")]

    for work_appointed in session.query(WorkList).filter(WorkList.director_id == current_user.id):
        temp = list()
        temp.append(work_appointed.id)
        temp.append(work_appointed.worker_url.user.get_full_name())
        temp.append(work_appointed.work_url.work)
        temp.append(str(work_appointed.work_start))
        if work_appointed.work_end is not None:
            temp.append(str(work_appointed.work_end))
        else:
            temp.append("Еще не назначена")

        work_status = session.query(WorkStatus).get(work_appointed.status)

        if work_status.id == 1:
            temp.append("Выполнена")
            temp.append(a_buttons_ready)
        elif work_status.id == 2:
            temp.append("Выполняется")
            temp.append(a_buttons_not_ready)
        elif work_status.id == 3:
            temp.append("Отказана")
            temp.append(a_buttons_ready)
        table_data.append(temp)

    return render_template('company.html', table_data=table_data)


@blueprint.route('/hire_workers')
def hire_workers():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)
    session = db_session.create_session()
    workers = session.query(Worker).filter(Worker.director_id == None).all()
    users_workers = [worker.user for worker in workers]
    buttons_a = [('Предложить работать', 'offer_to_work', 'primary')]
    return render_template('hire_workers.html', title="Биржа", users=users_workers, buttons_a=buttons_a)


@blueprint.route('/offer_to_work/<int:worker_id>')
def offer_to_work(worker_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)
    session = db_session.create_session()
    worker = session.query(Worker).get(worker_id)

    invites_from_director = session.query(DirectorInvite).filter(DirectorInvite.director_id == current_user.id,
                                                                 DirectorInvite.worker_id == worker.worker_id).first()
    if invites_from_director is not None:
        msg_type = 'danger'
        if invites_from_director.status_invite == '2':
            status = "Этот пользователь уже отказывал вам"
        elif invites_from_director.status_invite == '3':
            status = "Он уже работает на вас"
        else:
            status = "Вы уже приглашали его"

    elif worker.director_id is None:
        msg_type = 'success'
        status = "Ваше предложение ему отправилось"

        invite = DirectorInvite()
        invite.worker_id = worker_id
        invite.director_id = current_user.id

        session.add(invite)
        session.commit()
    else:
        msg_type = 'danger'
        status = "Этот пользователь уже работает"

    flash(status, msg_type)
    return redirect('/hire_workers')


@blueprint.route('/add_work', methods=["POST", "GET"])
def add_work():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)
    form = AddWork()
    if form.is_submitted():
        work = Work()
        work.work = form.work.data
        work.description = form.description.data
        work.director_id = current_user.id

        msg_type = 'success'
        status = "Работа успешно добавлена"
        session = db_session.create_session()

        try:
            session.add(work)
            session.commit()
            flash(status, msg_type)
            return redirect('/list_work')
        except:
            msg_type = 'danger'
            status = "Такое имя работы уже есть"
            flash(status, msg_type)

    return render_template('register.html', action_title="Добавление работы", form=form,
                           container_name='add_work_container')


@blueprint.route('/delete_work/<int:work_id>')
def delete_work(work_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    session = db_session.create_session()
    work = session.query(Work).get(work_id)

    if work.director_id != current_user.id or work is None:
        abort(404)

    session.delete(work)
    session.commit()

    flash("Работы удалена", "success")
    return redirect('/list_work')


@blueprint.route("/change_work/<int:work_id>", methods=["POST", "GET"])
def edit_work(work_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)
    session = db_session.create_session()
    work = session.query(Work).get(work_id)

    if work.director_id != current_user.id:
        abort(404)

    if work is None:
        abort(404)

    form = AddWork()

    if form.is_submitted():
        work.work = form.work.data
        work.description = form.description.data

        session.merge(work)
        try:
            session.commit()
            status = 'Работа изменена'
            msg_type = 'success'
            flash(status, msg_type)
            return redirect('/list_work')
        except:
            status = 'Выберите другое название'
            msg_type = 'danger'
            flash(status, msg_type)
    else:
        form.work.data = work.work
        form.description.data = work.description

    return render_template('register.html', action_title="Изменение работы", form=form,
                           container_name='add_work_container')


@blueprint.route("/appoint_work", methods=["POST", "GET"])
def appoint_work():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    form = AppointWork()
    session = db_session.create_session()

    form.work.choices = [(work.id, work.work) for work in
                         session.query(Work).filter(Work.director_id == current_user.id)]

    form.worker.choices = [
        (worker.worker_id, worker.user.get_full_name()) for worker in
        session.query(Worker).filter(Worker.director_id == current_user.id)]

    if form.is_submitted():
        appointed_work = WorkList()
        appointed_work.worker_id = form.data['worker']
        appointed_work.work_id = form.data['work']
        appointed_work.director_id = current_user.id
        session.add(appointed_work)
        session.commit()
        flash("Работа назначена", "success")
        return redirect('/')

    return render_template('register.html', action_title="Назначение работы", form=form,
                           container_name='appoint_work_container')


@blueprint.route('/list_work')
def list_work():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)
    session = db_session.create_session()
    works = session.query(Work).filter(Work.director_id == current_user.id)
    return render_template('works_list.html', works=works)


@blueprint.route('/workers_list')
def workers_list():
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    session = db_session.create_session()
    workers = session.query(Worker).filter(Worker.director_id == current_user.id)

    user_workers = [worker.user for worker in workers]
    buttons_a = [('Уволить', 'to_dismiss', 'danger')]

    return render_template('workers_list.html', users=user_workers, buttons_a=buttons_a)


@blueprint.route("/change_appoint_work/<int:worklist_id>", methods=["POST", "GET"])
def change_appoint_work(worklist_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    session = db_session.create_session()

    worklist = session.query(WorkList).get(worklist_id)
    if worklist is None or worklist.director_id != current_user.id:
        return abort(404)

    form = AppointWork()
    if form.is_submitted():
        worklist.worker_id = int(form.data['worker'])
        worklist.work_id = int(form.data['work'])
        session.merge(worklist)
        session.commit()
        flash("Изменения сделаны", "success")
        return redirect("/company")

    work_choices = [(worklist.work_id, worklist.work_url.work)]
    worker_choices = [(worklist.worker_id, worklist.worker_url.user.get_full_name())]

    for work_temp in session.query(Work).filter(Work.director_id == current_user.id,
                                                Work.id != worklist.work_id):
        work_choices.append((work_temp.id, work_temp.work))

    for worker in session.query(Director).get(current_user.id).workers:
        if worker.worker_id != worker_choices[0][0]:
            worker_choices.append((worker.worker_id, worker.user.get_full_name()))

    form.work.choices = work_choices
    form.worker.choices = worker_choices

    return render_template('register.html', action_title="Изменение назначенной работы", form=form,
                           container_name='appoint_work_container')


@blueprint.route('/delte_appoint_work/<int:worklist_id>')
def delete_appoint_work(worklist_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    session = db_session.create_session()
    worklist = session.query(WorkList).get(worklist_id)

    if worklist is None or worklist.director_id != current_user.id:
        abort(404)

    session.delete(worklist)
    session.commit()

    flash("Назначенная работа удалена", 'success')
    return redirect('/')

@blueprint.route("/get_result_appoint_work/<int:work_list_id>")
def get_result_work(work_list_id):
    if current_user.is_authenticated is False or current_user.account_type != 2:
        abort(404)

    session = db_session.create_session()

    work_list = session.query(WorkList).get(work_list_id)

    if work_list is None:
        abort(404)

    status = session.query(WorkStatus).get(work_list.status).name

    return render_template('result_page.html', status=status, msg=work_list.work_result_message)
