import base64

from app import db
from app.models import Sound, Tag, ThemeSong, User

BASIC = 'Basic ' + base64.b64encode(b'admin:admin').decode()
WRONG = 'Basic ' + base64.b64encode(b'admin:nope').decode()


def test_index_open(client):
    assert client.get('/').status_code == 200


def test_play_sound(client, silent_audio):
    r = client.get('/play/sounds/clip.wav')
    assert r.status_code == 200
    assert silent_audio == ['sounds/clip.wav']


def test_play_tag_returns_filename(client, app_ctx, silent_audio):
    tag = Tag(name='P')
    sound = Sound(filename='sounds/p.wav')
    db.session.add_all([tag, sound])
    db.session.commit()
    tag.sounds.append(sound)
    db.session.commit()

    r = client.get('/play/tag/P')
    assert r.status_code == 200
    assert r.data == b'sounds/p.wav'


def test_load_scans_files(client, app_ctx, tmp_path, monkeypatch):
    for rel in ['sounds/a.wav', 'sounds/JockJams/b.mp3', 'themes/t1.wav']:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'x')
    monkeypatch.chdir(tmp_path)

    r = client.get('/load')
    assert r.status_code == 200

    names = {s.filename for s in Sound.query.all()}
    tags = {t.name for t in Tag.query.all()}
    themes = ThemeSong.query.all()
    assert names == {'sounds/a.wav', 'sounds/b.mp3'}
    assert tags == {'JockJams'}
    assert len(themes) == 1
    # the subdirectory file is flattened into sounds/ (empty dir may remain)
    assert (tmp_path / 'sounds' / 'b.mp3').exists()
    if (tmp_path / 'sounds' / 'JockJams').is_dir():
        assert list((tmp_path / 'sounds' / 'JockJams').iterdir()) == []


def test_admin_requires_basic_auth(client):
    r = client.get('/admin')
    assert r.status_code == 401
    assert r.headers.get('WWW-Authenticate', '').startswith('Basic')
    assert client.get('/admin', headers={'Authorization': WRONG}).status_code == 401


def test_admin_allows_configured_creds(client, app_ctx):
    r = client.get('/admin/', headers={'Authorization': BASIC})
    assert r.status_code == 200
    users = User.query.filter_by(urole='ADMIN').all()
    assert len(users) == 1
    assert users[0].nickname == 'admin'


def test_admin_session_opens_user_pages(client):
    client.get('/admin/', headers={'Authorization': BASIC})
    assert client.get('/user/admin').status_code == 200
    assert client.get('/edit').status_code == 200


def test_modelview_is_accessible(app_ctx):
    from flask import g
    from app import views

    admin_user = User(nickname='admin', urole='ADMIN')
    user = User(nickname='bob', urole='USER')
    db.session.add_all([admin_user, user])
    db.session.commit()

    mv = views.SoundModelView(Sound, db)
    g.user = admin_user
    assert mv.is_accessible() is True
    g.user = user
    assert mv.is_accessible() is False
