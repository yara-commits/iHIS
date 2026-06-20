from flask import Flask
from config import config
from extensions import db, login_manager, migrate, mail
import os


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page'
    login_manager.login_message_category = 'warning'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('database', exist_ok=True)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth
    from routes.patient import patient
    from routes.doctor import doctor
    from routes.appointment import appointment
    from routes.admin import admin
    from routes.superadmin import superadmin
    from routes.laboratory import laboratory
    from routes.radiology import radiology
    from routes.pharmacy import pharmacy
    from routes.nursing import nursing
    from routes.reception import reception
    from routes.dental import dental
    from routes.rehabilitation import rehabilitation
    from routes.reports import reports

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(patient, url_prefix='/patients')
    app.register_blueprint(doctor, url_prefix='/doctors')
    app.register_blueprint(appointment, url_prefix='/appointments')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(superadmin, url_prefix='/superadmin')
    app.register_blueprint(laboratory, url_prefix='/lab')
    app.register_blueprint(radiology, url_prefix='/radiology')
    app.register_blueprint(pharmacy, url_prefix='/pharmacy')
    app.register_blueprint(nursing, url_prefix='/nursing')
    app.register_blueprint(reception, url_prefix='/reception')
    app.register_blueprint(dental, url_prefix='/dental')
    app.register_blueprint(rehabilitation, url_prefix='/rehab')
    app.register_blueprint(reports, url_prefix='/reports')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)