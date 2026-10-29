# midipad.py
#
#  Standalone MIDI control pad driver. Runs outside the app and fires
#  HTTP requests at the running soundboard:
#
#     uv run python midipad.py
#
#  Uses the default MIDI input device (or: python midipad.py --device N).

import logging
import sys
from urllib.parse import quote

import pygame
import pygame.midi
from pygame.locals import KEYDOWN, QUIT
import urllib3

from config import SERVER_NAME, TAGMAP
from app.decorators import asynctask

#
#  Midi control pad stuff goes here:
#

chromatic = range(36, 81)  # Values for the "Chromatic" preset, 36 through 80

PADMAP = chromatic

# Fallback tag when the pressed key has no entry in TAGMAP
DEFAULT = 'random'

logging.basicConfig(level=logging.DEBUG)

_conn = urllib3.PoolManager(maxsize=10)


@asynctask
def fireoff(urlToFetch):
    _conn.request('GET', urlToFetch)


def input_main(device_id=None):
    try:
        pygame.init()
        pygame.fastevent.init()
        pygame.midi.init()
    except Exception as error:
        logging.warning('MIDI input unavailable: %s', error)
        return

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id
    if input_id is None or input_id == -1:  # -1 is pygame's "no device" sentinel
        logging.warning('no default MIDI input device')
        return

    logging.info("using midi input_id :%s:", input_id)
    i = pygame.midi.Input(input_id)
    event_get = pygame.fastevent.get
    event_post = pygame.fastevent.post

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
                # CC 176 (volume slider) intentionally not handled
                if e.dict['status'] == 144:  # 144 is note on
                    logging.info('key %s pressed', e.dict['data1'])
                    try:
                        tagToPlay = TAGMAP[PADMAP.index(e.dict['data1'])]
                    except Exception:
                        logging.warning('no tag defined for that key, playing default')
                        tagToPlay = DEFAULT
                    logging.info('play tag %s', tagToPlay)
                    urlToFetch = 'http://' + SERVER_NAME + '/play/tag/' + quote(tagToPlay)
                    logging.info(urlToFetch)
                    fireoff(urlToFetch)

        if i.poll():
            midi_events = i.read(10)

            # convert them into pygame events
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    pygame.midi.quit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_main(device_id=int(sys.argv[1]))
    else:
        input_main()
