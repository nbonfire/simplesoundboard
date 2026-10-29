#config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'soundboardtags.sqlite')
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# HTTP Basic auth for the admin panel, "user:password"
BASIC_AUTH = os.environ.get('SOUNDBOARD_BASIC_AUTH', 'admin:admin')

# Enable the MIDI control-pad listener (requires a MIDI input device)
MIDI_INPUT_ENABLED = os.environ.get('SOUNDBOARD_MIDI') == '1'

# mail server settings (error logging)
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['nick@bonfatti.net', 'zillioxj@gmail.com']
