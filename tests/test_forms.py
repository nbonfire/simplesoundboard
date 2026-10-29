import os
import subprocess
import sys

import pytest

from app import db
from app.models import User


def test_editform_rejects_taken_nickname(app_ctx):
    from app import app
    from app.forms import EditForm

    db.session.add(User(nickname='admin', urole='ADMIN'))
    db.session.commit()

    with app.test_request_context():
        form = EditForm(original_nickname='someone')
        form.nickname.data = 'admin'
        form.themesong.data = ''
        assert form.validate() is False

        form = EditForm(original_nickname='admin')
        form.nickname.data = 'admin'
        form.themesong.data = ''
        assert form.validate() is True

        form = EditForm(original_nickname='admin')
        form.nickname.data = ''
        form.themesong.data = ''
        assert form.validate() is False


def test_midi_thread_not_started_by_default():
    from app import views
    assert views._midi_started is False


def test_midi_enabled_without_device_skips_cleanly():
    import pygame.midi
    try:
        pygame.midi.init()
        if pygame.midi.get_count() > 0:
            pytest.skip('MIDI device present on this host')
        pygame.midi.quit()
    except Exception as e:
        pytest.skip('cannot init pygame.midi on this host: %r' % (e,))

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ, SOUNDBOARD_MIDI='1', SDL_AUDIODRIVER='dummy', SDL_VIDEODRIVER='dummy')
    r = subprocess.run(
        [sys.executable, '-c', 'import app'],
        cwd=repo, env=env, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
