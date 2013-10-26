import pygame
import glob
import os
from flask import Flask, render_template, url_for

SERVER_NAME='0.0.0.0'
SERVER_PORT=5000

app = Flask(__name__)

pygame.mixer.init()


@app.route("/")
def index():
	return render_template('soundboard.html', filenamesandcategories=categoriesAndTheirFiles, jqueryurl=url_for('static', filename='js/jquery.min.js'))
	
@app.route("/play/<category>/<name>")
def play(category,name):
	name=os.path.join('sounds',category,name)
	#print name
	pygame.mixer.music.load(name)
	pygame.mixer.music.play()
	#sounds[name].play()
	return "ok"


def stripfilename(filename):
	
	noextension=os.path.splitext(filename)[0]
	separateCamelCase = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', noextension)
	return separateCamelCase.replace("_"," ")
 
if __name__ == '__main__':
	#fixSounds()
	filenames = glob.glob('sounds/*/*.wav')
	filenames.extend(glob.glob('sounds/*/*.mp3'))
	print filenames
	

	filenamesdictlist=[{'category':os.path.basename(os.path.dirname(a)), 'file':os.path.basename(a)} for a in filenames]
	categories=set([a['category'] for a in filenamesdictlist])
	categoriesAndTheirFiles=[{'category':x, 'sounds':[{'file': y['file'], 'name': stripfilename(y['file'])} for y in filenamesdictlist if y['category']==x]} for x in categories]
	#basenames=[os.path.basename(a) for a in filenames]
	print filenames


	#sounds=dict(zip(map(os.path.basename,filenames),map(pygame.mixer.Sound,filenames)))
	app.debug = True
	app.run(SERVER_NAME, SERVER_PORT)
