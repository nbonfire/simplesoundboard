import pygame
import glob
import os
from flask import Flask, render_template, url_for

SERVER_NAME=0.0.0.0
SERVER_PORT=5000

app = Flask(__name__)

pygame.mixer.init()

"""
from MediaInfoDLL import MediaInfo, Stream
from pydub import AudioSegment
import shutil

MI = MediaInfo()

def fixSounds():
	filenamestofix = glob.glob('incoming/*.wav')
	filenamestofix.extend(glob.glob('incoming/*.mp3'))
	basenamestofix=[os.path.basename(a) for a in filenamestofix]
	tocopy=[]
	toconvert=[]
	for wav in basenamestofix:
		a=MI.Open(os.path.join('incoming',wav))
		print wav
		audioformat=MI.Get(Stream.Audio,0,'Format')
		if audioformat =='PCM':
			#copy to sounds folder
			shutil.move(os.path.join('incoming',wav), os.path.join('sounds',wav))
			tocopy.append(wav)
		else:
			#convert to PCM, then copy to sounds folder

			#converted=AudioSegment.from_mp3(os.path.join('incoming',wav))
			#converted.export(os.path.join('sounds',wav[:4]+".wav"),format="wav")
			toconvert.append(wav)
	print "Needs converted: %s" % toconvert
	print "Copied without conversion: %s" % tocopy

			

"""

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



 
if __name__ == '__main__':
	#fixSounds()
	filenames = glob.glob('sounds/*/*.wav')
	filenames.extend(glob.glob('sounds/*/*.mp3'))
	print filenames
	

	filenamesdictlist=[{'category':os.path.basename(os.path.dirname(a)), 'file':os.path.basename(a)} for a in filenames]
	categories=set([a['category'] for a in filenamesdictlist])
	categoriesAndTheirFiles=[{'category':x, 'files':[y['file'] for y in filenamesdictlist if y['category']==x]} for x in categories]
	#basenames=[os.path.basename(a) for a in filenames]
	print filenames


	#sounds=dict(zip(map(os.path.basename,filenames),map(pygame.mixer.Sound,filenames)))
	app.debug = True
	app.run(SERVER_NAME, SERVER_PORT)
