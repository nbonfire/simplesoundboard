#!flask/bin/python
from app import app
#from config import SERVER_NAME, SERVER_PORT
# debug mode
#app.run(host='0.0.0.0', port=80, debug = True)
# gevent wsgi
from gevent.wsgi import WSGIServer

'''
http_server = WSGIServer(('john-htpc', 80), app)
http_server.serve_forever()
'''
