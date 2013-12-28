#!flask/bin/python
from app import app
from config import SERVER_NAME, SERVER_PORT
app.run(SERVER_NAME, SERVER_PORT, debug = True)