import pygame
import glob
import os
from flask import Flask, render_template

app = Flask(__name__)

pygame.mixer.init()

filenames = glob.glob('sounds/*.wav')
print filenames
filenames.extend(glob.glob('sounds/*.mp3'))
filenames=[os.path.basename(a) for a in filenames]
print filenames
page=""
for name in filenames:
	page= page + "<a href='/play/%s'>%s</a><br>"% (name,name)
print page


@app.route("/")
def index():
	return render_template('soundboard.html', filenames=filenames)
	
@app.route("/play/<name>")
def play(name):
	name=os.path.join('sounds',name)
	pygame.mixer.music.load(name)
	pygame.mixer.music.play()
	return "ok"




if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
