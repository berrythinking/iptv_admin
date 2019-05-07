import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required

from app import service, get_runtime_folder
from app.service.forms import ServiceSettingsForm
from app.service.service_settings import ServiceSettings
from .forms import ActivateForm


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    service.activate(lic)
    return redirect(url_for('UserView:dashboard'))


def _add_service(method: str):
    server = ServiceSettings()
    form = ServiceSettingsForm(obj=server)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
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
class ServiceView(FlaskView):
    route_base = "/service"

    @login_required
    def connect(self):
        service.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        service.disconnect()
        return redirect(url_for('UserView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            return activate_service(form)

        return render_template('user/activate.html', form=form)

    @login_required
    def stop(self):
        service.stop(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def ping(self):
        service.ping()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def get_log(self):
        service.get_log_service()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def view_log(self):
        path = os.path.join(get_runtime_folder(), service.id)
        try:
            with open(path, "r") as f:
                content = f.read()

            return content
        except OSError as e:
            print('Caught exception OSError : {0}'.format(e))
            return '''<pre>Not found, please use get log button firstly.</pre>'''

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
            server.delete()
        return jsonify(status='ok'), 200

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return edit_service(request.method, server)

        response = {"status": "failed"}
        return jsonify(response), 404

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
