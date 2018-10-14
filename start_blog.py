#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from blog import app


http_server = WSGIServer(('', 5001), app)
http_server.serve_forever()
