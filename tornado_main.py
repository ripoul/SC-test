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
import tornado.web
import tornado.wsgi
from scTest.wsgi import application as django_app


class MainHandler(tornado.web.RequestHandler):
    clients = set()

    def open(self):
        # logging.info('Client connected')
        MainHandler.clients.add(self)

    def on_message(self, message):
        # logging.log('Received message')
        MainHandler.broadcast(message)

    def on_close(self):
        # logging.info('Client disconnected')
        if self in MainHandler.clients:
            MainHandler.clients.remove(self)

    @classmethod
    def broadcast(cls, message):
        for client in cls.clients:
            client.write_message(message)


def make_app():
    return tornado.web.Application(
        [
            (r"/ws", MainHandler),
            (
                r"/(.*)",
                tornado.web.FallbackHandler,
                dict(fallback=tornado.wsgi.WSGIContainer(django_app)),
            ),
        ],
        debug=True,
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
