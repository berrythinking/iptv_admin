import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from app import get_runtime_folder
from app.service.forms import ServiceSettingsForm, ActivateForm
from app.service.service_entry import ServiceSettings


# routes
class ServiceView(FlaskView):
    route_base = "/service/"

    @login_required
    def connect(self):
        server = current_user.get_current_server()
        if server:
            server.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        server = current_user.get_current_server()
        if server:
            server.disconnect()
        return redirect(url_for('UserView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            server = current_user.get_current_server()
            if server:
                if not form.validate_on_submit():
                    return render_template('user/activate.html', form=form)

                lic = form.license.data
                server.activate(lic)
                return redirect(url_for('UserView:dashboard'))

        return render_template('user/activate.html', form=form)

    @login_required
    def stop(self):
        server = current_user.get_current_server()
        if server:
            server.stop(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def ping(self):
        server = current_user.get_current_server()
        if server:
            server.ping()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def get_log(self):
        server = current_user.get_current_server()
        if server:
            server.get_log_service()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def view_playlist(self):
        server = current_user.get_current_server()
        if server:
            return '<pre>{0}</pre>'.format(server.view_playlist())
        return '''<pre>Not found, please create server firstly.</pre>'''

    @login_required
    def view_log(self):
        server = current_user.get_current_server()
        if server:
            path = os.path.join(get_runtime_folder(), server.id)
            try:
                with open(path, "r") as f:
                    content = f.read()

                return content
            except OSError as e:
                print('Caught exception OSError : {0}'.format(e))
                return '''<pre>Not found, please use get log button firstly.</pre>'''
        return '''<pre>Not found, please create server firstly.</pre>'''

    # broadcast routes

    @login_required
    @route('/add', methods=['GET', 'POST'])
    def add(self):
        model = ServiceSettings()
        form = ServiceSettingsForm(request.form, obj=model)
        if request.method == 'POST' and form.validate_on_submit():
            form.populate_obj(model)
            model = model.save()
            current_user.add_server(model)
            return jsonify(status='ok'), 200

        return render_template('service/add.html', form=form)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        server = ServiceSettings.objects(id=sid).first()
        if server:
            server.delete()
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        form = ServiceSettingsForm(request.form, obj=server)

        if request.method == 'POST' and form.validate_on_submit():
            form.save()
            return jsonify(status='ok'), 200

        return render_template('service/edit.html', form=form)

    @route('/log/<sid>', methods=['POST'])
    def log(self, sid):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_folder(), sid)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(b'<pre>')
            f.write(data)
            f.write(b'</pre>')
            f.close()
        return jsonify(status='ok'), 200
