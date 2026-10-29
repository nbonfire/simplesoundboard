import pytest

from app import db, views
from app.models import Sound, Tag


def _tag_with_sounds(name, n=2):
    tag = Tag(name=name)
    sounds = [Sound(filename='sounds/%s%d.wav' % (name.lower(), i)) for i in range(n)]
    db.session.add_all([tag] + sounds)
    db.session.commit()
    for s in sounds:
        tag.sounds.append(s)
    db.session.commit()
    return tag, sounds


def test_dedup_same_source_within_window(app_ctx, silent_audio, monkeypatch):
    tag, (s1, s2) = _tag_with_sounds('Dedup')
    # Force a different pick on every fresh query to prove the cache is used.
    picks = iter([s1, s2, s1, s2])
    monkeypatch.setattr(Tag, 'randomsound', lambda self: next(picks))

    f1 = views.playtagunwrapped('Dedup', '1.1.1.1')
    f2 = views.playtagunwrapped('Dedup', '1.1.1.1')
    assert f1 == f2 == s1.filename


def test_dedup_independent_sources(app_ctx, silent_audio):
    _tag_with_sounds('Dedup2')
    f1 = views.playtagunwrapped('Dedup2', '1.1.1.1')
    f2 = views.playtagunwrapped('Dedup2', '2.2.2.2')
    assert f1 and f2
    assert '1.1.1.1' in views.playtagunwrapped.sources
    assert '2.2.2.2' in views.playtagunwrapped.sources


def test_random_tag_resolves_sound(app_ctx, silent_audio):
    _tag_with_sounds('OnlyTag')
    f = views.playtagunwrapped('random', '3.3.3.3')
    assert f.startswith('sounds/') and f.endswith('.wav')


def test_music_tags_play_on_music_channel(app_ctx, monkeypatch):
    fx_plays, music_plays = [], []

    class _Fx:
        def play(self, snd):
            fx_plays.append(snd[1])

    class _Music:
        def play(self, snd):
            music_plays.append(snd[1])

    monkeypatch.setattr(views, 'fxchannel', _Fx())
    monkeypatch.setattr(views, 'musicchannel', _Music())
    monkeypatch.setattr(views.pygame.mixer, 'get_init', lambda: True)
    monkeypatch.setattr(views.pygame.mixer, 'Sound', lambda name: ('SND', name))

    _tag_with_sounds('*JockJams')  # in MUSICTAGS
    _tag_with_sounds('NiceGoal')   # not in MUSICTAGS
    f_music = views.playtagunwrapped('*JockJams', '4.4.4.4')
    f_fx = views.playtagunwrapped('NiceGoal', '4.4.4.4')
    assert music_plays == [f_music]
    assert fx_plays == [f_fx]
