import os

from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from app.constants import StreamType
from app import get_runtime_stream_folder
from app.stream.stream_forms import EncodeStreamForm, RelayStreamForm, TimeshiftRecorderStreamForm, CatchupStreamForm, \
    TimeshiftPlayerStreamForm, TestLifeStreamForm


# routes
class StreamView(FlaskView):
    route_base = "/stream/"

    @login_required
    @route('/start', methods=['POST'])
    def start(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.start_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/stop', methods=['POST'])
    def stop(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.stop_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/restart', methods=['POST'])
    def restart(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.restart_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/get_log', methods=['POST'])
    def get_log(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.get_log_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

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
        server = current_user.get_current_server()
        if server:
            stream = server.make_relay_stream()
            form = RelayStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/relay/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/encode', methods=['GET', 'POST'])
    def add_encode(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_encode_stream()
            form = EncodeStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/timeshift_recorder', methods=['GET', 'POST'])
    def add_timeshift_recorder(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_timeshift_recorder_stream()
            form = TimeshiftRecorderStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/timeshift_recorder/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir(),
                                   timeshift_dir=stream.generate_timeshift_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/test_life', methods=['GET', 'POST'])
    def add_test_life(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_test_life_stream()
            form = TestLifeStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/test_life/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/catchup', methods=['GET', 'POST'])
    def add_catchup(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_catchup_stream()
            form = CatchupStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/catchup/add.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                                   timeshift_dir=stream.generate_timeshift_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/timeshift_player', methods=['GET', 'POST'])
    def add_timeshift_player(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_timeshift_player_stream()
            form = TimeshiftPlayerStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/timeshift_player/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = current_user.get_current_server()
        if server:
            stream = server.find_stream_by_id(sid)
            if stream:
                type = stream.get_type()
                if type == StreamType.RELAY:
                    form = RelayStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/relay/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == StreamType.ENCODE:
                    form = EncodeStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/encode/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == StreamType.TIMESHIFT_RECORDER:
                    form = TimeshiftRecorderStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/timeshift_recorder/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir(),
                                           timeshift_dir=stream.generate_timeshift_dir())
                elif type == StreamType.CATCHUP:
                    form = CatchupStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/catchup/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir(),
                                           timeshift_dir=stream.generate_timeshift_dir())
                elif type == StreamType.TIMESHIFT_PLAYER:
                    form = TimeshiftPlayerStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/timeshift_player/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == StreamType.TEST_LIFE:
                    form = TestLifeStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/test_life/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())

        return jsonify(status='failed'), 404

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.remove_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

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
