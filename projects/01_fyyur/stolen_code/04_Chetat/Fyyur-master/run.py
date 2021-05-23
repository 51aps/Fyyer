from app import create_app
from config import Config
from models import db
import logging
from logging import Formatter, FileHandler
from app import format_datetime

app = create_app(Config)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

app.jinja_env.filters['datetime'] = format_datetime

if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
      )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

if __name__ == '__main__':
    db.create_all(app=app)
    app.run()
