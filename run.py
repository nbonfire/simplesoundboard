#!flask/bin/python
from app import app
#from config import SERVER_NAME, SERVER_PORT
app.run(host='0.0.0.0', port=80,debug = False)
