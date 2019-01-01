from flask import render_template, redirect, url_for, request, session
from flask_login import logout_user, login_required, current_user

from app.user import user, cloud

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
