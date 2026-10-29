#!/usr/bin/env python3
import os

from app import app

port = int(os.environ.get('SOUNDBOARD_PORT', '80'))
app.run(host='0.0.0.0', port=port, debug=False)
