import os

import pytest

# Tests must never start the MIDI listener thread.
os.environ['SOUNDBOARD_MIDI'] = ''

from app import app, db  # noqa: E402


@pytest.fixture(scope='session')
def _db_uri(tmp_path_factory):
    return 'sqlite:///' + str(tmp_path_factory.mktemp('db') / 'test.sqlite')


@pytest.fixture
def client(_db_uri):
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['BASIC_AUTH'] = 'admin:admin'

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.drop_all()


@pytest.fixture
def app_ctx(_db_uri):
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.drop_all()


@pytest.fixture(autouse=True)
def _reset_playback_state():
    from app import views
    views.playtagunwrapped.sources = []
    views.playtagunwrapped.lasttag = {}
    views.playtagunwrapped.lasttagfilename = {}
    views.playtagunwrapped.lasttagtime = {}
    yield


@pytest.fixture
def silent_audio(monkeypatch):
    """Stub the pygame channel/sound layer and record requested filenames."""
    from app import views

    plays = []

    class _Channel:
        def play(self, snd):
            plays.append(snd[1])

    monkeypatch.setattr(views, 'fxchannel', _Channel())
    monkeypatch.setattr(views.pygame.mixer, 'get_init', lambda: True)
    monkeypatch.setattr(views.pygame.mixer, 'Sound', lambda name: ('SND', name))
    return plays
