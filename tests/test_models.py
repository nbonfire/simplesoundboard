from app import db
from app.models import Sound, Tag, User, get_or_create, stripfilename


def test_stripfilename():
    # original double-space quirk: space inserted at the underscore-adjacent capital
    assert stripfilename('sounds/Hitz_ClipOne.wav') == 'Hitz  Clip One'
    assert stripfilename('sounds/random.mp3') == 'random'


def test_get_or_create(app_ctx):
    a = get_or_create(Sound, filename='sounds/x.wav')
    b = get_or_create(Sound, filename='sounds/x.wav')
    assert a.id == b.id
    assert a.name == 'x'


def test_sound_tag_m2m(app_ctx):
    tag = Tag(name='CloseGame')
    sound = Sound(filename='sounds/one.wav')
    db.session.add_all([tag, sound])
    db.session.commit()
    tag.sounds.append(sound)
    db.session.commit()

    assert sound in list(tag.sounds)
    assert sound.tags[0].name == 'CloseGame'


def test_tag_randomsound(app_ctx):
    tag = Tag(name='RT')
    sounds = [Sound(filename='sounds/r%d.wav' % i) for i in range(3)]
    db.session.add_all([tag] + sounds)
    db.session.commit()
    for s in sounds:
        tag.sounds.append(s)
    db.session.commit()

    pick = tag.randomsound()
    assert pick in sounds


def test_make_unique_nickname(app_ctx):
    db.session.add(User(nickname='nick', urole='USER'))
    db.session.commit()
    assert User.make_unique_nickname('nick') == 'nick2'
    assert User.make_unique_nickname('fresh') == 'fresh'


def test_is_admin(app_ctx):
    admin = User(nickname='admin', urole='ADMIN')
    user = User(nickname='bob', urole='USER')
    db.session.add_all([admin, user])
    db.session.commit()
    assert admin.is_admin()
    assert not user.is_admin()
