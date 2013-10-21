import pygame
import cherrypy
import glob

pygame.mixer.init()

filenames = glob.glob('*.wav')
print filenames
filenames.extend(glob.glob('*.mp3'))
print filenames
page=""
for name in filenames:
	page= page + "<a href='/play/%s'>%s</a><br>"% (name,name)
print page
class HitzBoard(object):
	
	def index(self):
		
		return page
	index.exposed = True
	
	def play(self, name):
		pygame.mixer.music.load(name)
		pygame.mixer.music.play()
		return page
	play.exposed = True

cherrypy.quickstart(HitzBoard())


if __name__ == '__main__':
	cherrypy.server.socket_host='0.0.0.0'
	cherrypy.quickstart(HitzBoard())
