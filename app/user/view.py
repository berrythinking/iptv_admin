import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import logout_user, login_required, current_user

from app import client, service, get_runtime_folder
from app.home.forms import SettingsForm
from .forms import ActivateForm


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    client.activate(lic)
    return redirect(url_for('UserView:dashboard'))


# routes
class UserView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
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
    def ping_service(self):
        client.ping_service()
        return redirect(url_for('UserView:dashboard'))

    @route('/service_log/<filename>', methods=['POST'])
    def service_log(self, filename):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_folder(), filename)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(data)
            f.close()
        return jsonify(status='ok'), 200
