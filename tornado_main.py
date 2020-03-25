#!/usr/bin/env python

# Javascript Usage:
# var ws = new WebSocket('ws://localhost:8000/ws');
# ws.onopen = function(event){ console.log('socket open'); }
# ws.onclose = function(event){ console.log('socket closed'); }
# ws.onerror = function(error){ console.log('error:', err); }
# ws.onmessage = function(event){ console.log('message:', event.data); }
# # ... wait for connection to open
# ws.send('hello world')

import tornado.ioloop
import tornado.websocket
import tornado.web
import tornado.wsgi
from scTest.wsgi import application as django_app

import os


class MainHandler(tornado.websocket.WebSocketHandler):
    clients = []

    def open(self):
        self.clients.append(self)
        print("WebSocket opened")

    def on_message(self, message):
        print("rec : " + message)
        self.broadcast_message(message)

    def on_close(self):
        self.clients.remove(self)
        print("WebSocket closed")

    def broadcast_message(self, message):
        for client in self.clients:
            client.write_message(message)


def make_app():
    return tornado.web.Application(
        [
            (r"/ws", MainHandler),
            (
                r"/static/(.*)",
                tornado.web.StaticFileHandler,
                dict(path=os.path.join(os.path.dirname(__file__), "static")),
            ),
            (
                r"/(.*)",
                tornado.web.FallbackHandler,
                dict(fallback=tornado.wsgi.WSGIContainer(django_app)),
            ),
        ],
        debug=True,
    )


application = make_app()
application = tornado.wsgi.WSGIAdapter(application)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("app runing on http://localhost:8888/")
    tornado.ioloop.IOLoop.current().start()
