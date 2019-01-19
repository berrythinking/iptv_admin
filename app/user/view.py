from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify, current_app
from flask_login import logout_user, login_required, current_user
import app.constants as constants

from app.home.stream_entry import EncodeStream, RelayStream, make_relay_stream, make_encode_stream
from .forms import SettingsForm, ActivateForm, EncodeStreamEntryForm, RelayStreamEntryForm


def get_runtime_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    return locale


def _add_relay_stream(method: str):
    stream = make_relay_stream()
    form = RelayStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        current_app.streams_holder.add_stream(new_entry)
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
        current_app.streams_holder.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_encode_stream(method: str, stream: EncodeStream):
    form = EncodeStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('user/stream/encode/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    current_app.cloud.activate(lic)
    return redirect(url_for('UserView:dashboard'))


# routes
class UserView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
        streams = current_app.streams_holder.get_streams()
        return render_template('user/dashboard.html', streams=streams, status=current_app.cloud.status())

    @route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings(self):
        form = SettingsForm(obj=current_user.settings)
        if request.method == 'POST':
            if form.validate_on_submit():
                form.update_settings(current_user.settings)
                current_user.save()
                return render_template('user/settings.html', form=form)

        return render_template('user/settings.html', form=form)

    @route('/logout')
    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('HomeView:index'))

    @route('/connect')
    @login_required
    def connect(self):
        current_app.cloud.connect()
        return redirect(url_for('UserView:dashboard'))

    @route('/disconnect')
    @login_required
    def disconnect(self):
        current_app.cloud.disconnect()
        return redirect(url_for('UserView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            return activate_service(form)

        return render_template('user/activate.html', form=form)

    # stop service
    @route('/stop_service')
    @login_required
    def stop_service(self):
        current_app.cloud.stop_service(1)
        return redirect(url_for('UserView:dashboard'))

    # stop service
    @route('/ping_service')
    @login_required
    def ping_service(self):
        current_app.cloud.ping_service()
        return redirect(url_for('UserView:dashboard'))

    # stream
    @route('/stream/add_relay', methods=['GET', 'POST'])
    @login_required
    def add_relay_stream(self):
        return _add_relay_stream(request.method)

    @route('/stream/add_encode', methods=['GET', 'POST'])
    @login_required
    def add_encode_stream(self):
        return _add_encode_stream(request.method)

    @route('/stream/edit/<sid>', methods=['GET', 'POST'])
    @login_required
    def edit_stream(self, sid):
        stream = current_app.streams_holder.find_stream_by_id(sid)
        if stream:
            if stream.type == constants.StreamType.RELAY:
                return edit_relay_stream(request.method, stream)
            elif stream.type == constants.StreamType.ENCODE:
                return edit_encode_stream(request.method, stream)

        response = {"status": "failed"}
        return jsonify(response), 404

    @route('/stream/remove', methods=['POST'])
    @login_required
    def remove_stream(self):
        sid = request.form['sid']
        current_app.streams_holder.remove_stream(sid)
        response = {"sid": sid}
        return jsonify(response), 200

    @route('/stream/start', methods=['POST'])
    @login_required
    def start_stream(self):
        sid = request.form['sid']
        stream = current_app.streams_holder.find_stream_by_id(sid)
        if stream:
            current_app.cloud.start_stream(stream.config())

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/stream/stop', methods=['POST'])
    @login_required
    def stop_stream(self):
        sid = request.form['sid']
        stream = current_app.streams_holder.find_stream_by_id(sid)
        if stream:
            current_app.cloud.stop_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/stream/restart', methods=['POST'])
    @login_required
    def restart_stream(self):
        sid = request.form['sid']
        stream = current_app.streams_holder.find_stream_by_id(sid)
        if stream:
            current_app.cloud.restart_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200
