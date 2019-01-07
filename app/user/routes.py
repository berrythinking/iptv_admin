from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import logout_user, login_required, current_user

from app.user import user, cloud, streams
from app import socketio
from app.home.stream_entry import StreamEntry

from .forms import SettingsForm, ActivateForm, StreamEntryForm


def get_runtime_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    return locale


def add_stream_entry(method: str):
    form = StreamEntryForm()
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        streams.append(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/add.html', form=form)


def edit_stream_entry(method: str, entry: StreamEntry):
    form = StreamEntryForm(obj=entry)

    if method == 'POST' and form.validate_on_submit():
        entry = form.update_entry(entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/edit.html', form=form)


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    return render_template('user/dashboard.html', streams=streams)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user.settings)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.update_settings(current_user.settings)
            current_user.save()
            return render_template('user/settings.html', form=form)

    return render_template('user/settings.html', form=form)


@user.route('/logout')
@login_required
def logout():
    session.pop('currency', None)
    logout_user()
    return redirect(url_for('home.start'))


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    license = form.license.data
    cloud.activate(license)
    return dashboard()


@user.route('/activate', methods=['POST', 'GET'])
@login_required
def activate():
    form = ActivateForm()
    if request.method == 'POST':
        return activate_service(form)

    return render_template('user/activate.html', form=form)


# stop service
@user.route('/stop_service')
@login_required
def stop_service():
    cloud.stop_service(1)
    return dashboard()


# stop service
@user.route('/ping_service')
@login_required
def ping_service():
    cloud.ping_service()
    return dashboard()


# stream
@user.route('/stream/add', methods=['GET', 'POST'])
@login_required
def add_stream():
    return add_stream_entry(request.method)


@user.route('/stream/edit/<mid>', methods=['GET', 'POST'])
@login_required
def edit_stream(mid):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            return edit_stream_entry(request.method, entry)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/stream/remove', methods=['POST'])
@login_required
def remove_stream():
    stream_id = request.form['stream_id']
    response = {"stream_id": stream_id}
    return jsonify(response), 200


# socketio
@socketio.on('test')
def socketio_test(message):
    print(message)


@socketio.on('connect')
def socketio_connect():
    print('Client connected')
    socketio.emit('newnumber', {'number': 11})


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')
