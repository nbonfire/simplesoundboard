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
