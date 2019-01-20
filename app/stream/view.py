from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required

import app.constants as constants

from app import socketio
from app.user import cloud, streams_holder

from .stream_entry import EncodeStream, RelayStream, make_relay_stream, make_encode_stream
from .forms import EncodeStreamEntryForm, RelayStreamEntryForm


def _add_relay_stream(method: str):
    stream = make_relay_stream()
    form = RelayStreamEntryForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        streams_holder.add_stream(new_entry)
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
        streams_holder.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_encode_stream(method: str, stream: EncodeStream):
    form = EncodeStreamEntryForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        stream.save()
        return jsonify(status='ok'), 200

    return render_template('stream/encode/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


# routes
class StreamView(FlaskView):
    route_base = "/stream/"

    @route('/add_relay', methods=['GET', 'POST'])
    @login_required
    def add_relay_stream(self):
        return _add_relay_stream(request.method)

    @route('/add_encode', methods=['GET', 'POST'])
    @login_required
    def add_encode_stream(self):
        return _add_encode_stream(request.method)

    @route('/edit/<sid>', methods=['GET', 'POST'])
    @login_required
    def edit_stream(self, sid):
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            if stream.type == constants.StreamType.RELAY:
                return edit_relay_stream(request.method, stream)
            elif stream.type == constants.StreamType.ENCODE:
                return edit_encode_stream(request.method, stream)

        response = {"status": "failed"}
        return jsonify(response), 404

    @route('/remove', methods=['POST'])
    @login_required
    def remove_stream(self):
        sid = request.form['sid']
        streams_holder.remove_stream(sid)
        response = {"sid": sid}
        return jsonify(response), 200

    @route('/start', methods=['POST'])
    @login_required
    def start_stream(self):
        sid = request.form['sid']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            cloud.start_stream(stream.config())

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/stop', methods=['POST'])
    @login_required
    def stop_stream(self):
        sid = request.form['sid']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            cloud.stop_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200

    @route('/restart', methods=['POST'])
    @login_required
    def restart_stream(self):
        sid = request.form['sid']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            cloud.restart_stream(sid)

        response = {"sid": sid}
        return jsonify(response), 200


# socketio
@socketio.on('connect')
def socketio_connect():
    print('Client connected')


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')
