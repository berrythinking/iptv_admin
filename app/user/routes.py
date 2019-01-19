from flask import render_template, redirect, url_for, request, jsonify
from flask_login import logout_user, login_required, current_user
import json
import app.constants as constants

from app.user import user, cloud
from app import socketio
from app.home.stream_holder import StreamsHolder
from app.home.stream_entry import EncodeStream, RelayStream, make_relay_stream, make_encode_stream
from .forms import SettingsForm, ActivateForm, EncodeStreamEntryForm, RelayStreamEntryForm
from .stream_handler import IStreamHandler
from app.client.client_constants import Commands, Status

streams_holder = StreamsHolder()


class StreamHandler(IStreamHandler):
    def __init__(self):
        pass

    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus(params['status'])

        params_str = json.dumps(params)
        socketio.emit(Commands.STATISTIC_STREAM_COMMAND, params_str)

    def on_stream_sources_changed(self, params: dict):
        # sid = params['id']
        params_str = json.dumps(params)
        socketio.emit(Commands.CHANGED_STREAM_COMMAND, params_str)

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        params_str = json.dumps(params)
        socketio.emit(Commands.STATISTIC_SERVICE_COMMAND, params_str)

    def on_quit_status_stream(self, params: dict):
        # sid = params['id']
        # stream = streams_holder.find_stream_by_id(sid)

        params_str = json.dumps(params)
        socketio.emit(Commands.QUIT_STATUS_STREAM_COMMAND, params_str)

    def on_client_state_changed(self, status: Status):
        pass


stream_handler = StreamHandler()
cloud.set_handler(stream_handler)


def get_runtime_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    return locale


def _add_relay_stream(method: str):
    stream = make_relay_stream()
    form = RelayStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        streams_holder.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/relay/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_relay_stream(method: str, stream: RelayStream):
    form = RelayStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('user/stream/relay/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_encode_stream(method: str):
    stream = make_encode_stream()
    form = EncodeStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        streams_holder.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_encode_stream(method: str, stream: EncodeStream):
    form = EncodeStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('user/stream/encode/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    streams = streams_holder.get_streams()
    return render_template('user/dashboard.html', streams=streams, status=cloud.status())


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

    lic = form.license.data
    cloud.activate(lic)
    return redirect(url_for('user.dashboard'))


@user.route('/connect')
@login_required
def connect():
    cloud.connect()
    return redirect(url_for('user.dashboard'))


@user.route('/disconnect')
@login_required
def disconnect():
    cloud.disconnect()
    return redirect(url_for('user.dashboard'))


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
    return redirect(url_for('user.dashboard'))


# stop service
@user.route('/ping_service')
@login_required
def ping_service():
    cloud.ping_service()
    return redirect(url_for('user.dashboard'))


# stream
@user.route('/stream/add_relay', methods=['GET', 'POST'])
@login_required
def add_relay_stream():
    return _add_relay_stream(request.method)


@user.route('/stream/add_encode', methods=['GET', 'POST'])
@login_required
def add_encode_stream():
    return _add_encode_stream(request.method)


@user.route('/stream/edit/<sid>', methods=['GET', 'POST'])
@login_required
def edit_stream(sid):
    stream = streams_holder.find_stream_by_id(sid)
    if stream:
        if stream.type == constants.StreamType.RELAY:
            return edit_relay_stream(request.method, stream)
        elif stream.type == constants.StreamType.ENCODE:
            return edit_encode_stream(request.method, stream)

    response = {"status": "failed"}
    return jsonify(response), 404


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
        cloud.start_stream(stream.config())

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
