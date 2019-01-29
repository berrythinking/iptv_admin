import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import logout_user, login_required, current_user

from app import client, service, get_runtime_folder
from app.home.forms import SettingsForm
from app.service.forms import ServiceSettingsForm
from app.service.service_settings import ServiceSettings
from .forms import ActivateForm


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    client.activate(lic)
    return redirect(url_for('UserView:dashboard'))


def _add_service(method: str):
    server = ServiceSettings()
    form = ServiceSettingsForm(obj=server)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_settings()
        new_entry.save()
        return jsonify(status='ok'), 200

    return render_template('service/add.html', form=form)


def edit_service(method: str, server: ServiceSettings):
    form = ServiceSettingsForm(obj=server)

    if method == 'POST' and form.validate_on_submit():
        server = form.update_entry(server)
        server.save()
        return jsonify(status='ok'), 200

    return render_template('service/edit.html', form=form)


# routes
class UserView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
        # services = ServiceSettings.objects()
        # services_choices = []
        # for serv in services:
        #    services_choices.append((str(serv.id), serv.name))

        streams = service.get_streams()
        front_streams = []
        for stream in streams:
            front_streams.append(stream.to_front())
        return render_template('user/dashboard.html', streams=front_streams, client=client.to_front(),
                               service=service.to_front())

    @route('/settings', methods=['POST', 'GET'])
    @login_required
    def settings(self):
        form = SettingsForm(obj=current_user.settings)

        if request.method == 'POST':
            if form.validate_on_submit():
                form.update_settings(current_user.settings)
                current_user.save()
                return render_template('user/settings.html', form=form)

        return render_template('user/settings.html', form=form)

    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('HomeView:index'))

    @login_required
    def connect(self):
        client.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        client.disconnect()
        return redirect(url_for('UserView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            return activate_service(form)

        return render_template('user/activate.html', form=form)

    @login_required
    def stop_service(self):
        client.stop_service(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def get_log_service(self):
        client.get_log_service(service.id)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def view_log_service(self):
        path = os.path.join(get_runtime_folder(), service.id)
        try:
            with open(path, "r") as f:
                content = f.read()

            return content
        except OSError as e:
            return '''<pre>Not found, please use get log button firstly.</pre>'''

    @login_required
    def ping_service(self):
        client.ping_service()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    @route('/add/service', methods=['GET', 'POST'])
    def add_service(self):
        return _add_service(request.method)

    @route('/edit/<sid>', methods=['GET', 'POST'])
    @login_required
    def edit_service(self, sid):
        server = service.find_server_by_id(sid)
        if server:
            return edit_service(request.method, server)

        response = {"status": "failed"}
        return jsonify(response), 404

    @route('/service_log/<filename>', methods=['POST'])
    def service_log(self, filename):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_folder(), filename)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(b'<pre>')
            f.write(data)
            f.write(b'</pre>')
            f.close()
        return jsonify(status='ok'), 200
