from flask_classy import FlaskView, route
from flask import send_from_directory, render_template, request, flash
from flask_mail import Message
from app import app, mail

import app.constants as constants
from app.home.forms import ContactForm


def send_email(email: str, subject: str, message: str):
    config = app.config['PUBLIC_CONFIG']
    msg = Message(subject, recipients=[config['support']['contact_email']])
    msg.body = 'From: {0} <{0}> {1}'.format(email, message)
    mail.send(msg)


class HomeView(FlaskView):
    route_base = "/"

    def index(self):
        languages = constants.AVAILABLE_LOCALES_PAIRS
        return render_template('index.html', languages=languages)

    @route('/robots.txt')
    @route('/sitemap.xml')
    def static_from_root(self):
        return send_from_directory(self.route_base, request.path[1:])

    @route('/contact', methods=['GET', 'POST'])
    def contact(self):
        form = ContactForm()

        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('All fields are required.')
                return render_template('contact.html', form=form)

            send_email(form.email.data, form.subject.data, form.message.data)
            return render_template('contact.html', success=True)

        elif request.method == 'GET':
            return render_template('contact.html', form=form)
