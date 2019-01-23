from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required

import app.constants as constants

from app import client, service

from .stream_entry import EncodeStream, RelayStream, TimeshiftRecorderStream, make_relay_stream, make_encode_stream, \
    make_timeshift_recorder_stream
from .forms import EncodeStreamEntryForm, RelayStreamEntryForm, TimeshiftRecorderStreamEntryForm


def _add_relay_stream(method: str):
    stream = make_relay_stream()
    form = RelayStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/relay/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_relay_stream(method: str, stream: RelayStream):
    form = RelayStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('stream/relay/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_encode_stream(method: str):
    stream = make_encode_stream()
    form = EncodeStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_encode_stream(method: str, stream: EncodeStream):
    form = EncodeStreamEntryForm(obj=stream)

    if method == 'POST':  # FIXME form.validate_on_submit()
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('stream/encode/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_timeshift_recorder_stream(method: str):
    stream = make_timeshift_recorder_stream()
    form = TimeshiftRecorderStreamEntryForm(obj=stream)
    if method == 'POST':  # FIXME form.validate_on_submit()
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_recorder/add.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                           timeshift_dir=stream.generate_timeshift_dir())


def edit_timeshift_recorder_stream(method: str, stream: TimeshiftRecorderStream):
    form = TimeshiftRecorderStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_recorder/edit.html', form=form,
                           feedback_dir=stream.generate_feedback_dir(), timeshift_dir=stream.generate_timeshift_dir())


# routes
class StreamView(FlaskView):
    route_base = "/stream/"

    @login_required
    @route('/add/relay', methods=['GET', 'POST'])
    def add_relay_stream(self):
        return _add_relay_stream(request.method)

    @login_required
    @route('/add/encode', methods=['GET', 'POST'])
    def add_encode_stream(self):
        return _add_encode_stream(request.method)

    @login_required
    @route('/add/timeshift_recorder', methods=['GET', 'POST'])
    def add_timeshift_recorder_stream(self):
        return _add_timeshift_recorder_stream(request.method)

    @route('/edit/<sid>', methods=['GET', 'POST'])
    @login_required
    def edit_stream(self, sid):
        stream = service.find_stream_by_id(sid)
        if stream:
            if stream.type == constants.StreamType.RELAY:
                return edit_relay_stream(request.method, stream)
            elif stream.type == constants.StreamType.ENCODE:
                return edit_encode_stream(request.method, stream)
            elif stream.type == constants.StreamType.TIMESHIFT_RECORDER:
                return edit_timeshift_recorder_stream(request.method, stream)

        response = {"status": "failed"}
        return jsonify(response), 404

    @route('/remove', methods=['POST'])
    @login_required
    def remove_stream(self):
        sid = request.form['sid']
        service.remove_stream(sid)
        response = {"sid": sid}
        return jsonify(response), 200

    @route('/start', methods=['POST'])
    @login_required
    def start_stream(self):
        sid = request.form['sid']
        stream = service.find_stream_by_id(sid)
        if stream:
            client.start_stream(stream.config())

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/stop', methods=['POST'])
    @login_required
    def stop_stream(self):
        sid = request.form['sid']
        stream = service.find_stream_by_id(sid)
        if stream:
            client.stop_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/restart', methods=['POST'])
    @login_required
    def restart_stream(self):
        sid = request.form['sid']
        stream = service.find_stream_by_id(sid)
        if stream:
            client.restart_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200
