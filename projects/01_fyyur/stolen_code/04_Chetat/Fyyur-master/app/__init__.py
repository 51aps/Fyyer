import dateutil.parser
import babel
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
moment = Moment()


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


def create_app(config):
    app = Flask(__name__)
    # App init was here
    app.config.from_object(config)

    initialize_extensions(app)
    register_blueprints(app)
    migrate = Migrate(app, db)
    return app


def initialize_extensions(app):
    moment.init_app(app)
    db.init_app(app)


def register_blueprints(app):
    from app.views import bp
    app.register_blueprint(bp)