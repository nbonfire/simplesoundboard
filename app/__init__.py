from flask import Flask 
from flask.ext.sqlalchemy import SQLAlchemy 
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.admin import Admin
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'soundboard failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/soundboard.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('soundboard startup')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view='login'

oid = OpenID(app, os.path.join(basedir, 'tmp'))

admin = Admin(app, name='HitzBoard Admin')

from app import views, models

def get_or_create(model, **kwargs):
	instance = db.session.query(model).filter_by(**kwargs).first()
	if instance:
		return instance
	else:
		instance = model(**kwargs)
		db.session.add(instance)
		db.session.commit()
		return instance

soundfilenames = glob.glob('sounds/*.wav')
soundfilenames.extend(glob.glob('sounds/*.mp3'))
#print filenames


for filename in soundfilenames:
	afile=get_or_create(Sound, filename=filename)

themefilenames = glob.glob('themes/*.wav')
themefilenames.extend(glob.glob('themes/*.mp3'))

for filename in themefilenames:
	afile=get_or_create(ThemeSong, filename=filename)
