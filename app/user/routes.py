from flask import render_template, redirect, url_for, request, jsonify
from flask_login import logout_user, login_required, current_user

from app.user import user, cloud
from app import socketio
from app.home.stream_entry import StreamsHolder, Stream

from .forms import SettingsForm, ActivateForm, StreamEntryForm
import app.constants as constants

streams_holder = StreamsHolder()


def get_runtime_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    return locale


def add_stream_entry(method: str):
    stream = Stream()
    form = StreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        streams_holder.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_stream_entry(method: str, stream: Stream):
    form = StreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('user/stream/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    streams = streams_holder.get_streams()
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
    logout_user()
    return redirect(url_for('home.start'))


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    license = form.license.data
    cloud.activate(license)
    return dashboard()


@user.route('/connect')
@login_required
def connect():
    cloud.connect()
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


@user.route('/stream/edit/<sid>', methods=['GET', 'POST'])
@login_required
def edit_stream(sid):
    stream = streams_holder.find_stream_by_id(sid)
    if stream:
        return edit_stream_entry(request.method, stream)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/stream/remove', methods=['POST'])
@login_required
def remove_stream():
    sid = request.form['sid']
    streams_holder.remove_stream(sid)
    response = {"sid": sid}
    return jsonify(response), 200


@user.route('/stream/start', methods=['POST'])
@login_required
def start_stream():
    sid = request.form['sid']
    stream = streams_holder.find_stream_by_id(sid)
    if stream:
        cloud.start_stream(stream.generate_feedback_dir(), stream.log_level, stream.config())

    response = {"sid": sid}
    return jsonify(response), 200


@user.route('/stream/stop', methods=['POST'])
@login_required
def stop_stream():
    sid = request.form['sid']
    stream = streams_holder.find_stream_by_id(sid)
    if stream:
        cloud.stop_stream(sid)

    response = {"sid": sid}
    return jsonify(response), 200


@user.route('/stream/restart', methods=['POST'])
@login_required
def restart_stream():
    sid = request.form['sid']
    stream = streams_holder.find_stream_by_id(sid)
    if stream:
        cloud.restart_stream(sid)

    response = {"sid": sid}
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
