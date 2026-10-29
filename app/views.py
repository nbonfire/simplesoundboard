import base64
import glob
import os
import queue
from datetime import datetime, timedelta, timezone

import pygame
import pygame.midi
from pygame.locals import KEYDOWN, QUIT

from flask import Response, flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.sql.expression import func

from app import admin, app, db, lm
from config import basedir
from app.decorators import asynctask
from app.forms import EditForm
from app.models import Sound, Tag, ThemeSong, User, get_or_create, stripfilename

pygame.mixer.init()
fxchannel = pygame.mixer.Channel(1)
clock = pygame.time.Clock()

TAGMAP = ['*Waiting',
          '*TrashTalk',
          'FunnyMusic',
          'random',
          '*Comeback',
          '*Blowout',
          '*CloseGame',
          '*GameOver',
          '*Windowshopping',
          '*Fuckup',
          '*BigSave',
          '*FireExtinguished',
          '*NiceGoal',
          '*JockJams',
          '*OneTimer',
          '*OnFire',
          ]

_theme_queue = queue.Queue()
_entrance_played = False
_midi_started = False


def _basic_authenticated():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(header[6:]).decode('utf-8')
    except Exception:
        return False
    return decoded == app.config['BASIC_AUTH']


def _login_admin():
    """Sign in the single admin user, creating it (with a random theme) on first use."""
    global _entrance_played
    user = User.query.filter_by(urole='ADMIN').first()
    if user is None:
        user = User(nickname='admin', urole='ADMIN')
        if ThemeSong.query.count() > 0:
            user.theme = ThemeSong.random_themesong()
        db.session.add(user)
        db.session.commit()
    if user.hastheme() and not _entrance_played:
        _entrance_played = True
        entrance_queue(user.theme)
    login_user(user)
    return user


@app.before_request
def check_admin_auth():
    if not request.path.startswith('/admin'):
        return None
    if _basic_authenticated():
        _login_admin()
        return None
    response = Response('Authentication required', 401)
    response.headers['WWW-Authenticate'] = 'Basic realm="HitzBoard Admin"'
    return response


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now(timezone.utc)
        db.session.add(g.user)
        db.session.commit()


@app.route("/")
@app.route("/index")
def index():
    global TAGMAP
    groups = list(zip(*[iter(TAGMAP)]*4))
    tags = [item for sublist in reversed(groups) for item in sublist]
    tagsandsounds = [{
        'category': x,
        'sounds': [
            {'file': y.filename, 'name': y.name} for y in sorted(x.sounds, key=lambda s: s.name)
        ]
    } for x in db.session.query(Tag).order_by(Tag.name).all()]
    return render_template('soundboard.html', tags=tags,
                           filenamesandcategories=tagsandsounds,
                           jqueryurl=url_for('static', filename='js/jquery.min.js'))


@app.route('/load')
def loadsounds():
    soundfilenames = glob.glob('sounds/*.wav')
    soundfilenames.extend(glob.glob('sounds/*.mp3'))

    for filename in soundfilenames:
        get_or_create(Sound, filename=filename)

    themefilenames = glob.glob('themes/*.wav')
    themefilenames.extend(glob.glob('themes/*.mp3'))

    for filename in themefilenames:
        get_or_create(ThemeSong, filename=filename)

    subdir_sounds = glob.glob('sounds/*/*.wav')
    subdir_sounds.extend(glob.glob('sounds/*/*.mp3'))

    for f in subdir_sounds:
        newname = os.path.join('sounds', os.path.basename(f))
        tagname = os.path.relpath(os.path.dirname(f), 'sounds')
        tag = get_or_create(Tag, name=tagname)
        os.rename(f, newname)
        asound = get_or_create(Sound, filename=newname)
        if tag not in asound.tags:
            asound.tags.append(tag)
            db.session.commit()
    return "ok"


@app.route("/play/sounds/<name>")
def play(name):
    global fxchannel
    name = os.path.join('sounds', name)
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    fxchannel.play(pygame.mixer.Sound(name))
    return "ok"


@app.route("/play/tag/<tagname>")
def playtag(tagname):
    return playtagunwrapped(tagname, request.remote_addr or 'anonymous')


def playtagunwrapped(tagname, source):
    global fxchannel
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if source in playtagunwrapped.sources:
        if (tagname != playtagunwrapped.lasttag[source]) or (
                datetime.now(timezone.utc) > (playtagunwrapped.lasttagtime[source] + timedelta(seconds=3))):
            if tagname == 'random':
                tag = Tag.query.order_by(func.random()).first()
            else:
                tag = get_or_create(Tag, name=tagname)
            filetoplay = tag.randomsound().filename
            playtagunwrapped.lasttag[source] = tagname
            playtagunwrapped.lasttagfilename[source] = filetoplay
            playtagunwrapped.lasttagtime[source] = datetime.now(timezone.utc)
        else:
            filetoplay = playtagunwrapped.lasttagfilename[source]
            playtagunwrapped.lasttagtime[source] = datetime.now(timezone.utc)
    else:
        if tagname == 'random':
            tag = Tag.query.order_by(func.random()).first()
        else:
            tag = get_or_create(Tag, name=tagname)
        filetoplay = tag.randomsound().filename
        playtagunwrapped.sources.append(source)
        playtagunwrapped.lasttag[source] = tagname
        playtagunwrapped.lasttagfilename[source] = filetoplay
        playtagunwrapped.lasttagtime[source] = datetime.now(timezone.utc)

    fxchannel.play(pygame.mixer.Sound(filetoplay))
    return filetoplay



playtagunwrapped.sources = []
playtagunwrapped.lasttag = {}
playtagunwrapped.lasttagfilename = {}
playtagunwrapped.lasttagtime = {}


@lm.user_loader
def load_user(id):
    return db.session.get(User, int(id))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(original_nickname=g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.theme = ThemeSong.query.filter_by(name=form.themesong.data).first()
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        if g.user.theme is not None:
            form.themesong.data = g.user.theme.name
    return render_template('edit.html', form=form)


class SoundModelView(ModelView):
    column_display_all_relations = True
    column_list = ('name', 'tags')
    form_excluded_columns = ('name',)

    def is_accessible(self):
        return bool(g.user.is_authenticated and g.user.is_admin())

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.name = stripfilename(model.filename)
        db.session.add(model)


class ThemeSongModelView(ModelView):
    column_list = ('name', 'users')
    form_excluded_columns = ('name',)

    def is_accessible(self):
        return bool(g.user.is_authenticated and g.user.is_admin())

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.name = stripfilename(model.filename)
        db.session.add(model)


class SoundFileAdmin(FileAdmin):
    allowed_extensions = ('wav', 'mp3', 'ogg')

    def is_accessible(self):
        return bool(g.user.is_authenticated and g.user.is_admin())

    def on_file_upload(self, directory, path, filename, storage_name, file):
        db.session.add(Sound(filename=filename))
        db.session.commit()


class ThemeSongFileAdmin(FileAdmin):
    allowed_extensions = ('wav', 'mp3', 'ogg')

    def is_accessible(self):
        return bool(g.user.is_authenticated and g.user.is_admin())

    def on_file_upload(self, directory, path, filename, storage_name, file):
        db.session.add(ThemeSong(filename=filename))
        db.session.commit()


class UserModelView(ModelView):
    can_create = False
    form_args = dict(
        urole=dict(
            choices=[('USER', 'USER'), ('ADMIN', 'ADMIN')]))

    def is_accessible(self):
        return bool(g.user.is_authenticated and g.user.is_admin())


admin.add_view(SoundModelView(Sound, db))
admin.add_view(ThemeSongModelView(ThemeSong, db, name="Theme Songs"))
admin.add_view(ModelView(Tag, db))
admin.add_view(UserModelView(User, db))
admin.add_view(SoundFileAdmin(os.path.join(basedir, 'sounds'), '/sounds/', name='Upload Sounds'))
admin.add_view(ThemeSongFileAdmin(os.path.join(basedir, 'themes'), '/themes/', name='Upload Theme Songs'))


#
#  Entrance theme (theme song) playback:
#

@asynctask
def entrance_queue(theme):
    global _theme_queue
    controller = False
    if _theme_queue.empty():
        controller = True
    _theme_queue.put(theme)
    if controller:
        while pygame.mixer.music.get_busy():
            clock.tick(10)
        if _theme_queue.empty() == False and pygame.mixer.music.get_busy() == False:
            pygame.mixer.music.load(_theme_queue.get().filename)
            _theme_queue.task_done()
        while _theme_queue.empty() == False:
            pygame.mixer.music.queue(_theme_queue.get().filename)
            _theme_queue.task_done()
        pygame.mixer.music.play()


#
#  Midi control pad stuff:
#

chromatic = range(36, 81)  # Values for the "Chromatic" preset, 36 through 80

PADMAP = chromatic

# Hardcoded favorite tags to use on the pad.
DEFAULT = 'random'


@asynctask
def input_main(device_id=None):
    global _midi_started
    try:
        pygame.init()
        pygame.fastevent.init()
        pygame.midi.init()
    except Exception as error:
        app.logger.warning('MIDI input disabled: %s', error)
        return

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id
    if input_id is None:
        app.logger.warning('MIDI input disabled: no default MIDI input device')
        return

    app.logger.info('using midi input_id: %s', input_id)
    i = pygame.midi.Input(input_id)
    _midi_started = True
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
                if e.dict['status'] == 144:  # 144 is note on
                    try:
                        tagToPlay = TAGMAP[PADMAP.index(e.dict['data1'])]
                        app.logger.info('play tag %s', tagToPlay)
                    except Exception:
                        app.logger.warning('no tag defined for pad %s, playing default',
                                           e.dict['data1'])
                        tagToPlay = DEFAULT
                    playtagunwrapped(tagToPlay, source='midi')
                # CC 176 (volume slider) intentionally not handled

        if i.poll():
            midi_events = i.read(10)

            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    pygame.midi.quit()
