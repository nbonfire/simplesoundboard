#midipad.py


#
#  Midi control pad stuff goes here:
#

chromatic = range(36,81) # Values for the "Chromatic" preset, 36 through 80

PADMAP = chromatic

# Eventually I'll implement a "favorites" in the model to replace this. For now, hardcoded favorite tags to use on the mpd.



DEFAULT = 'random'

import sys
import os
import urllib2
from config import SERVER_NAME, TAGMAP
import pygame
import pygame.midi
from pygame.locals import *



def input_main(device_id = None):
	pygame.init()
	pygame.fastevent.init()
	event_get = pygame.fastevent.get
	event_post = pygame.fastevent.post
	pygame.midi.init()

	#_print_device_info()


	if device_id is None:
		input_id = pygame.midi.get_default_input_id()
	else:
		input_id = device_id

	print ("using midi input_id :%s:" % input_id)
	i = pygame.midi.Input( input_id )

	#pygame.display.set_mode((1,1))



	going = True
	while going:
		events = event_get()
		for e in events:
			if e.type in [QUIT]:
				going = False
			if e.type in [KEYDOWN]:
				going = False
			if e.type in [pygame.midi.MIDIIN]:
				#
				# THIS IS WHERE ALL THE GOOD SHIT GOES
				#
				if e.dict['status']==176: #176 is the volume slider
					print 'volume adjust: '+str(e.dict['data2'])
					# lowest value 0, highest 127, stored in e.dict['data2']
					# TODO: add xbmc json-rpc clal to set volume based on this
					# For now, use nircmd and a system() call 
					volumeLevel=e.dict['data2']/127.0
					returnval=os.system('NirCmd.exe setappvolume xbmc.exe ' + str(volumeLevel))
				if e.dict['status']==144: #144 is key down
					print 'key '+str(e.dict['data1'])+' pressed'
					try:
						tagToPlay = TAGMAP[PADMAP.index(e.dict['data1'])]
						print 'play tag ' + tagToPlay
					except Exception, error:
						#raise e
						print error
						print 'no tag defined for that key, lets play a Jock Jam instead'
						tagToPlay = DEFAULT
					urlToFetch='http://'+SERVER_NAME+'/play/tag/'+urllib.quote(tagToPlay)
					print urlToFetch
					
					#response=playtagunwrapped(tagToPlay,source='midi')
					response=urllib2.urlopen(urlToFetch)
					

		if i.poll():
			midi_events = i.read(10)
			
			# convert them into pygame events.
			midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

			for m_e in midi_evs:
				event_post( m_e )

	del i
	pygame.midi.quit()



if __name__ == '__main__':
	input_main()
