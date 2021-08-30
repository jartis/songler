from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from app import app

app.config['SCHEME'] = 'https'

http_server = WSGIServer(('0.0.0.0', 800), app)
http_server.serve_forever()