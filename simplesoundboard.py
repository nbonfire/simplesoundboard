import pygame
import glob
from flask import Flask

app = Flask(__name__)

pygame.mixer.init()

filenames = glob.glob('sounds/*.wav')
print filenames
filenames.extend(glob.glob('sounds/*.mp3'))
print filenames
page=""
for name in filenames:
	page= page + "<a href='/play/%s'>%s</a><br>"% (name,name)
print page


@app.route("/")
def index():
	return page
	
@app.route("/play/<name>")
def play(name):
	pygame.mixer.music.load(name)
	pygame.mixer.music.play()
	return page




if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
