import os
from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required

import app.constants as constants

from app import service, get_runtime_stream_folder

from .stream_entry import EncodeStream, RelayStream, TimeshiftRecorderStream, CatchupStream, TimeshiftPlayerStream
from .stream_forms import EncodeStreamForm, RelayStreamForm, TimeshiftRecorderStreamForm, CatchupStreamForm, \
    TimeshiftPlayerStreamForm, TestLifeStreamForm


def _add_relay_stream(method: str):
    stream = service.make_relay_stream()
    form = RelayStreamForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/relay/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_relay_stream(method: str, stream: RelayStream):
    form = RelayStreamForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/relay/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_encode_stream(method: str):
    stream = service.make_encode_stream()
    form = EncodeStreamForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_encode_stream(method: str, stream: EncodeStream):
    form = EncodeStreamForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/encode/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_timeshift_recorder_stream(method: str):
    stream = service.make_timeshift_recorder_stream()
    form = TimeshiftRecorderStreamForm(obj=stream)
    if method == 'POST':  # FIXME form.validate_on_submit()
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_recorder/add.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                           timeshift_dir=stream.generate_timeshift_dir())


def edit_timeshift_recorder_stream(method: str, stream: TimeshiftRecorderStream):
    form = TimeshiftRecorderStreamForm(obj=stream)

    if method == 'POST':  # FIXME form.validate_on_submit()
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_recorder/edit.html', form=form,
                           feedback_dir=stream.generate_feedback_dir(), timeshift_dir=stream.generate_timeshift_dir())


def _add_catchup_stream(method: str):
    stream = service.make_catchup_stream()
    form = CatchupStreamForm(obj=stream)
    if method == 'POST':  # FIXME form.validate_on_submit()
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/catchup/add.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                           timeshift_dir=stream.generate_timeshift_dir())


def edit_catchup_stream(method: str, stream: CatchupStream):
    form = CatchupStreamForm(obj=stream)

    if method == 'POST':  # FIXME form.validate_on_submit()
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/catchup/edit.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                           timeshift_dir=stream.generate_timeshift_dir())


def _add_timeshift_player_stream(method: str):
    stream = service.make_timeshift_player_stream()
    form = TimeshiftPlayerStreamForm(obj=stream)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_player/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_timeshift_player_stream(method: str, stream: TimeshiftPlayerStream):
    form = TimeshiftPlayerStreamForm(obj=stream)

    if method == 'POST' and form.validate_on_submit():
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/timeshift_player/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


def _add_test_life_stream(method: str):
    stream = service.make_test_life_stream()
    form = TestLifeStreamForm(obj=stream)
    if method == 'POST':  # FIXME form.validate_on_submit()
        new_entry = form.make_entry()
        service.add_stream(new_entry)
        return jsonify(status='ok'), 200

    return render_template('stream/test_life/add.html', form=form, feedback_dir=stream.generate_feedback_dir())


def edit_test_life_stream(method: str, stream: TimeshiftRecorderStream):
    form = TestLifeStreamForm(obj=stream)

    if method == 'POST':  # FIXME form.validate_on_submit()
        stream = form.update_entry(stream)
        service.update_stream(stream)
        return jsonify(status='ok'), 200

    return render_template('stream/test_life/edit.html', form=form, feedback_dir=stream.generate_feedback_dir())


# routes
class StreamView(FlaskView):
    route_base = "/stream/"

    @login_required
    @route('/start', methods=['POST'])
    def start(self):
        sid = request.form['sid']
        service.start_stream(sid)
        return jsonify(status='ok'), 200

    @login_required
    @route('/stop', methods=['POST'])
    def stop(self):
        sid = request.form['sid']
        service.stop_stream(sid)
        return jsonify(status='ok'), 200

    @login_required
    @route('/restart', methods=['POST'])
    def restart(self):
        sid = request.form['sid']
        service.restart_stream(sid)
        return jsonify(status='ok'), 200

    @login_required
    @route('/get_log', methods=['POST'])
    def get_log(self):
        sid = request.form['sid']
        service.get_log_stream(sid)
        return jsonify(status='ok'), 200

    @login_required
    def view_log(self, sid):
        path = os.path.join(get_runtime_stream_folder(), sid)
        try:
            with open(path, "r") as f:
                content = f.read()
                return content
        except OSError as e:
            print('Caught exception OSError : {0}'.format(e))
            return '''<pre>Not found, please use get log button firstly.</pre>'''

    # broadcast routes

    @login_required
    @route('/add/relay', methods=['GET', 'POST'])
    def add_relay(self):
        return _add_relay_stream(request.method)

    @login_required
    @route('/add/encode', methods=['GET', 'POST'])
    def add_encode(self):
        return _add_encode_stream(request.method)

    @login_required
    @route('/add/timeshift_recorder', methods=['GET', 'POST'])
    def add_timeshift_recorder(self):
        return _add_timeshift_recorder_stream(request.method)

    @login_required
    @route('/add/test_life', methods=['GET', 'POST'])
    def add_test_life(self):
        return _add_test_life_stream(request.method)

    @login_required
    @route('/add/catchup', methods=['GET', 'POST'])
    def add_catchup(self):
        return _add_catchup_stream(request.method)

    @login_required
    @route('/add/timeshift_player', methods=['GET', 'POST'])
    def add_timeshift_player(self):
        return _add_timeshift_player_stream(request.method)

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        stream = service.find_stream_by_id(sid)
        if stream:
            type = stream.get_type()
            if type == constants.StreamType.RELAY:
                return edit_relay_stream(request.method, stream)
            elif type == constants.StreamType.ENCODE:
                return edit_encode_stream(request.method, stream)
            elif type == constants.StreamType.TIMESHIFT_RECORDER:
                return edit_timeshift_recorder_stream(request.method, stream)
            elif type == constants.StreamType.CATCHUP:
                return edit_catchup_stream(request.method, stream)
            elif type == constants.StreamType.TIMESHIFT_PLAYER:
                return edit_timeshift_player_stream(request.method, stream)
            elif type == constants.StreamType.TEST_LIFE:
                return edit_test_life_stream(request.method, stream)

        response = {"status": "failed"}
        return jsonify(response), 404

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        service.remove_stream(sid)
        return jsonify(status='ok'), 200

    @route('/log/<sid>', methods=['POST'])
    def log(self, sid):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_stream_folder(), sid)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(b'<pre>')
            f.write(data)
            f.write(b'</pre>')
            f.close()

        return jsonify(status='ok'), 200
