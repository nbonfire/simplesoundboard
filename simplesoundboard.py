import pygame
import re
import glob
import os
from flask import Flask, render_template, url_for
from flask.ext.admin import Admin, BaseView, expose

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

SERVER_NAME='0.0.0.0'
SERVER_PORT=5000

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soundboardtags.sqlite'
app.config['SECRET_KEY'] = '123456790'
db = SQLAlchemy(app)

pygame.mixer.init()

sound_tags_table = db.Table('sound_tags', db.Model.metadata,
						db.Column('sound_id', db.Integer, db.ForeignKey('sound.id')),
						db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
						)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Unicode(64))

	def __str__(self):
		return self.name

class Sound(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename=db.Column(db.String(120))
	name=db.Column(db.String(120))
	tags = db.relationship('Tag', secondary=sound_tags_table, backref=db.backref('sounds', lazy='dynamic'))
	def __init__(self, filename=None, name=None):
		if filename==None:
			print "filename is none for some reason. %s" % self
		else:
			self.filename = filename
			if name == None:

				self.name = stripfilename(filename)
			else:
				self.name = name
	def __str__(self):
		return self.name


class SoundModelView(ModelView):
	form_excluded_columns = ('name')
	def on_model_change(self, form, model, is_created):
		
		
		
		if is_created==True:
			model.name=stripfilename(model.filename)


def get_or_create(session, model, **kwargs):
	instance = session.query(model).filter_by(**kwargs).first()
	if instance:
		return instance
	else:
		instance = model(**kwargs)
		session.add(instance)
		session.commit()
		return instance

@app.route("/")
def index():
	tagsandsounds=[{'category':x, 'sounds':[{'file': y.filename, 'name':y.name} for y in x.sounds]} for x in db.session.query(Tag).all() ]
	return render_template('soundboard.html', filenamesandcategories=tagsandsounds, jqueryurl=url_for('static', filename='js/jquery.min.js'))
	
@app.route("/play/<name>")
def play(name):
	name=os.path.join('sounds', name)
	#print name
	pygame.mixer.music.load(name)
	pygame.mixer.music.play()
	##sounds[name].play()
	return "ok"


def stripfilename(filename):
	basename=os.path.basename(filename)
	noextension=os.path.splitext(basename)[0] 
	separateCamelCase = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', noextension)
	return separateCamelCase.replace("_"," ")
 
admin = Admin(app, name='HitzBoard Admin')

admin.add_view(SoundModelView(Sound, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(FileAdmin(os.path.join(os.path.dirname(__file__), 'sounds'), '/sounds/', name = 'Sound Files'))

if __name__ == '__main__':
	#fixSounds()
	filenames = glob.glob('sounds/*.wav')
	filenames.extend(glob.glob('sounds/*.mp3'))
	print filenames
	

	#filenamesdictlist=[{'category':os.path.basename(os.path.dirname(a)), 'file':os.path.basename(a)} for a in filenames]
	#categories=set([a['category'] for a in filenamesdictlist])
	#categoriesAndTheirFiles=[{'category':x, 'sounds':[{'file': y['file'], 'name': stripfilename(y['file'])} for y in filenamesdictlist if y['category']==x]} for x in categories]
	#basenames=[os.path.basename(a) for a in filenames]
	print filenames

	for filename in filenames:
		afile=get_or_create(db.session, Sound, filename=filename)

	#sounds=dict(zip(map(os.path.basename,filenames),map(pygame.mixer.Sound,filenames)))
	app.debug = True
	app.run(SERVER_NAME, SERVER_PORT)
