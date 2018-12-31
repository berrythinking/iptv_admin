from flask import render_template, redirect, url_for, jsonify, request, session
from flask_login import logout_user, login_required, current_user

from app.user import user

from .forms import SettingsForm


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
