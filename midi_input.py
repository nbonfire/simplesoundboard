#!/usr/bin/env python3
"""
An input method for simplesoundboard to work with midi pad triggers such as the Akai MPD18

Adapted from the pygame midi.py example.

First, open the MPD18 editor and load the Chromatic preset, then press Commit-Upload to set the pads.
Adjust SERVER to be the hostname (and optionally port number) for your soundboard.
Adjust TAGMAP to be the names of effect tags you want to trigger.
Adjust DEFAULT to trigger a tag for an unknown pad value.

Usage:

python midi_input.py --input
"""

import sys

import pygame
import pygame.midi
from pygame.locals import KEYDOWN, QUIT
from urllib.parse import quote


SERVER = 'john-htpc'
# for future use. For now, leave URLROOT blank.
URLROOT = ''

chromatic = range(36, 81)  # Values for the "Chromatic" preset, 36 through 80

PADMAP = chromatic
TAGMAP = ['Jock Jams',
          'Big Save',
          'Blowout',
          'Close Game',
          'Comeback',
          'Fire Extinguished',
          'Fuckup',
          'Game Over',
          'Nice Goal',
          'On Fire',
          'One-Timer',
          'Waiting',
          'Windowshopping',
          'Wrongful Goal',
          ]

DEFAULT = 'Jock Jams'


def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()


def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
              (i, interf, name, opened, in_out))


def input_main(device_id=None):
    pygame.init()
    pygame.fastevent.init()
    event_get = pygame.fastevent.get
    event_post = pygame.fastevent.post

    pygame.midi.init()

    _print_device_info()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    pygame.display.set_mode((1, 1))

    going = True
    while going:
        events = event_get()
        for e in events:
            if e.type in [QUIT]:
                going = False
            if e.type in [KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                if e.dict['status'] == 144:  # 144 is key down
                    print('key ' + str(e.dict['data1']) + ' pressed')
                    try:
                        tagToPlay = TAGMAP[PADMAP.index(e.dict['data1'])]
                        print('play tag ' + tagToPlay)
                    except Exception:
                        print('no tag defined for that key, lets play a Jock Jam instead')
                        tagToPlay = DEFAULT
                    urlToFetch = 'http://' + SERVER + URLROOT + '/play/tag/' + quote(tagToPlay)
                    print(urlToFetch)

        if i.poll():
            midi_events = i.read(10)

            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    pygame.midi.quit()


def usage():
    print("--input [device_id] : Midi message logger")
    print("--output [device_id] : Midi piano keyboard")
    print("--list : list available midi devices")


if __name__ == '__main__':
    try:
        device_id = int(sys.argv[-1])
    except ValueError:
        device_id = None

    if "--input" in sys.argv or "-i" in sys.argv:
        input_main(device_id)
    elif "--output" in sys.argv or "-o" in sys.argv:
        usage()
    elif "--list" in sys.argv or "-l" in sys.argv:
        print_device_info()
    else:
        usage()
