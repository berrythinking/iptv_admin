from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request
from flask_login import logout_user, login_required, current_user

from app import service
from app.home.forms import SettingsForm
from app.service.service_settings import ServiceSettings


# routes
class UserView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
        server = ServiceSettings.objects().first()
        if server:
            service.set_settings(server)

            streams = service.get_streams()
            front_streams = []
            for stream in streams:
                front_streams.append(stream.to_front())
            serv = service.to_front()
            return render_template('user/dashboard.html', streams=front_streams, service=serv)

        return redirect(url_for('UserView:settings'))

    @route('/settings', methods=['POST', 'GET'])
    @login_required
    def settings(self):
        servers = ServiceSettings.objects()
        form = SettingsForm(obj=current_user.settings)

        if request.method == 'POST':
            if form.validate_on_submit():
                form.update_settings(current_user.settings)
                current_user.save()
                return render_template('user/settings.html', form=form, servers=servers)

        return render_template('user/settings.html', form=form, servers=servers)

    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('HomeView:index'))

    @login_required
    def remove(self):
        current_user.delete()
        return redirect(url_for('HomeView:index'))
