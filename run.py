#!flask/bin/python
from app import app
#from config import SERVER_NAME, SERVER_PORT
# debug mode
app.run(host='0.0.0.0', port=8888, debug = True)
# gevent wsgi
#from gevent.wsgi import WSGIServer

'''
http_server = WSGIServer(('127.0.0.1', 8888), app)
http_server.serve_forever()
'''