import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from app import get_runtime_folder, get_first_user_server
from app.service.forms import ServiceSettingsForm
from app.service.service_entry import ServiceSettings
from .forms import ActivateForm


# activate license
def _activate_server(server, form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    server.activate(lic)
    return redirect(url_for('UserView:dashboard'))


def _remove_server(server: ServiceSettings):
    server.delete()
    return jsonify(status='ok'), 200


def _add_service(method: str):
    server = ServiceSettings()
    form = ServiceSettingsForm(obj=server)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        new_entry.users.append(current_user.id)
        new_entry.save()
        current_user.add_server(new_entry)
        return jsonify(status='ok'), 200

    return render_template('service/add.html', form=form)


def _edit_service(method: str, server: ServiceSettings):
    form = ServiceSettingsForm(obj=server)

    if method == 'POST' and form.validate_on_submit():
        server = form.update_entry(server)
        server.save()
        return jsonify(status='ok'), 200

    return render_template('service/edit.html', form=form)


# routes
class ServiceView(FlaskView):
    route_base = "/service"

    @login_required
    def connect(self):
        server = get_first_user_server(current_user)
        if server:
            server.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        server = get_first_user_server(current_user)
        if server:
            server.disconnect()
        return redirect(url_for('UserView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            server = get_first_user_server(current_user)
            if server:
                return _activate_server(server, form)

        return render_template('user/activate.html', form=form)

    @login_required
    def stop(self):
        server = get_first_user_server(current_user)
        if server:
            server.stop(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def ping(self):
        server = get_first_user_server(current_user)
        if server:
            server.ping()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def get_log(self):
        server = get_first_user_server(current_user)
        if server:
            server.get_log_service()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def view_log(self):
        server = get_first_user_server(current_user)
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
        return _add_service(request.method)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return _remove_server(server)

        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return _edit_service(request.method, server)

        return jsonify(status='failed'), 404

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
