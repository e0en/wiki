#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from app import app


http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
