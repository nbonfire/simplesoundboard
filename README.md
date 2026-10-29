simplesoundboard
================

A simple soundboard server to be run on an HTPC with a web interface, MIDI control-pad support, and a basic-auth admin panel.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/):

    uv sync

Create the database (and apply migrations after model changes):

    uv run flask --app app db upgrade
    uv run flask --app app db migrate   # only after changing models

## Run

    uv run python run.py                 # serves on port 80
    SOUNDBOARD_PORT=8080 uv run python run.py

Environment variables:

- `SOUNDBOARD_PORT` — HTTP port (default 80)
- `SOUNDBOARD_BASIC_AUTH` — `"user:password"` protecting `/admin` (default `admin:admin`)
- `SOUNDBOARD_MIDI` — set to `1` to start the MIDI control-pad listener (needs a MIDI input device)

## Use

- Web UI: `GET /` — open on the LAN, no auth required.
- Admin panel: `GET /admin/` — HTTP Basic auth. Upload sound/theme files there, or drop files into `sounds/` and `themes/` and hit `GET /load` to import them.
- MIDI pad: load the "Chromatic" preset in the MPD18 editor, run with `SOUNDBOARD_MIDI=1`. `python midi_input.py --list` shows available devices.

## Tests

    uv run pytest
