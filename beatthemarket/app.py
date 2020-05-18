from werkzeug.contrib.fixers import ProxyFix

from flask import Flask, render_template
from itsdangerous import URLSafeTimedSerializer
from beatthemarket.blueprints.page import page
from beatthemarket.blueprints.news import news
from beatthemarket.blueprints.portfolio import portfolio
from beatthemarket.blueprints.portfolio.fetch import save_quote
from beatthemarket.blueprints.user.models import User
from beatthemarket.blueprints.user import user
from beatthemarket.extensions import (
    debug_toolbar, mail, csrf, db, login_manager, bcrypt, scheduler, celery
)


def create_app(settings_override=None):
    """
    Create a Flask application using the server factory pattern.

    :param settings_override: Override settings
    :return: Flask server
    """

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.logger.setLevel(app.config['LOG_LEVEL'])

    middleware(app)
    error_templates(app)
    app.register_blueprint(page)
    app.register_blueprint(news)
    app.register_blueprint(user)
    app.register_blueprint(portfolio)
    extensions(app)
    authentication(app, User)
    process_scheduler(scheduler, app)
    init_celery(app)
    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    scheduler.init_app(app)

    return None


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        if uid is not None:
            print('load_user, user_id is: ', uid)
            return user_model.query.get(uid)
        return None

    # @login_manager.request_loader
    def load_token(token):
        """
        Sometimes you want to login users without using cookies, such as using header values or an api key passed as a query argument. In these cases, you should use the request_loader callback. This callback should behave the same as your user_loader callback, except that it accepts the Flask request instead of a user_id.
        :param token:
        :return:
        """
        duration = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=duration)
        user_uid = data[0]

        return user_model.query.get(user_uid)


def process_scheduler(scheduler, app):
    """
    https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    """
    scheduler.add_job(id='sch1',
                      func=save_quote,
                      trigger='cron',
                      day_of_week='0-4',
                      hour='9-18',
                      minute='1,15,30,45',
                      timezone='EST',
                      args=[app])
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


def init_celery(app=None):
    app = app or create_app()
    celery.conf.BROKER_URL = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template(f'errors/{code}.html')

    for error in [404, 500]:
        app.errorhandler(error)(render_status)

    return None
