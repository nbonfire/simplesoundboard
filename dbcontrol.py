from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager 
from flask.ext.migrate import Migrate, MigrateCommand

from app import db,models

app = Flask(__name__)
app.config.from_object('config')

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()