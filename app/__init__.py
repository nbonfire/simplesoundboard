import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_migrate import Migrate

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler

    tmpdir = os.path.join(basedir, 'tmp')
    os.makedirs(tmpdir, exist_ok=True)
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER,
                               ADMINS, 'soundboard failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    file_handler = RotatingFileHandler(os.path.join(tmpdir, 'soundboard.log'),
                                       'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('soundboard startup')

db = SQLAlchemy(app)
migrate = Migrate(app, db, directory='migrations')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'admin.index'

admin = Admin(app, name='HitzBoard Admin')

# Soundboard content directories must exist for FileAdmin and /load
for _content_dir in ('sounds', 'themes'):
    os.makedirs(os.path.join(basedir, _content_dir), exist_ok=True)

from app import views, models  # noqa: E402

if app.config['MIDI_INPUT_ENABLED']:
    views.input_main()
