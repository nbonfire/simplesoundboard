#config.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))
"""
SERVER_NAME='0.0.0.0'
SERVER_PORT=5000
"""
SERVER_NAME='myserverurl'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'soundboardtags.sqlite')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['nick@bonfatti.net', 'zillioxj@gmail.com']

TAGMAP = ['*Waiting',
          '*TrashTalk',
          'Funny Music',
          'random',
          '*Comeback',
          '*Blowout',
          '*CloseGame',
          '*GameOver',
          '*Windowshopping',
          '*Fuckup',
          '*BigSave',
          '*FireExtinguished',
          '*NiceGoal',
          '*JockJams',
          '*OneTimer',
          '*OnFire',
          ]
MUSICTAGS = ['Funny Music', '*JockJams']
