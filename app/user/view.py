from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request
from flask_login import logout_user, login_required, current_user

from app import cloud, streams_holder, service
from app.home.forms import SettingsForm
from .forms import ActivateForm


# activate license
def activate_service(form: ActivateForm):
    if not form.validate_on_submit():
        return render_template('user/activate.html', form=form)

    lic = form.license.data
    cloud.activate(lic)
    return redirect(url_for('UserView:dashboard'))


# routes
class UserView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
        streams = streams_holder.get_streams()
        return render_template('user/dashboard.html', streams=streams, service=service.to_front(),
                               client=cloud.to_front())

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
        cloud.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        cloud.disconnect()
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
        cloud.stop_service(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def ping_service(self):
        cloud.ping_service()
        return redirect(url_for('UserView:dashboard'))
