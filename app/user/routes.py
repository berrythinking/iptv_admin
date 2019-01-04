from flask import render_template, redirect, url_for, request, session
from flask_login import logout_user, login_required, current_user

from app.user import user, cloud
from app import socketio

from .forms import SettingsForm, ActivateForm


def get_runtime_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    return locale


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    return render_template('user/dashboard.html')


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user.settings)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.update_settings(current_user.settings)
            current_user.save()
            return render_template('user/settings.html', form=form)

    return render_template('user/settings.html', form=form)


@user.route('/logout')
@login_required
def logout():
    session.pop('currency', None)
    logout_user()
    return redirect(url_for('home.start'))


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    license = form.license.data
    cloud.activate(license)
    return dashboard()


@user.route('/activate', methods=['POST', 'GET'])
@login_required
def activate():
    form = ActivateForm()
    if request.method == 'POST':
        return activate_service(form)

    return render_template('user/activate.html', form=form)


# stop service
@user.route('/stop_service')
@login_required
def stop_service():
    cloud.stop_service(1)
    return dashboard()


# stop service
@user.route('/ping_service')
@login_required
def ping_service():
    cloud.ping_service()
    return dashboard()


# socketio
@socketio.on('test')
def socketio_test(message):
    print(message)


@socketio.on('connect')
def socketio_connect():
    print('Client connected')
    socketio.emit('newnumber', {'number': 11})


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')
