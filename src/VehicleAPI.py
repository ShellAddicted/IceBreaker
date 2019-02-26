import logging
import threading
import asyncio
import json

try:
    import tornado.ioloop
    import tornado.gen
    import tornado.websocket
except ImportError:
    raise ImportError("Install tornado, example: #pip3 install tornado")


class VehicleAPI(threading.Thread):

    def __init__(self, url):
        super(VehicleAPI, self).__init__(name="VehicleAPI")
        self._url = url
        self._evt = threading.Event()
        self._ws = None

    @tornado.gen.coroutine
    def _wsReq(self, payload):
        try:
            self._ws.send_message(json.dumps(payload))
        except:
            return None
        msg = yield self._ws.read_message()
        if msg is None:
            logging.error("Received Empty Message")
            self._ws = None
            return None
        else:
            return msg

    def ping(self):
        return self._wsReq({"cmd": "ping", "args": []})

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())  # Create an async loop for the current Thread
        self._ws = None
        self._connect()
        tornado.ioloop.IOLoop.instance().start()

    @tornado.gen.coroutine
    def _connect(self):
        while self._evt:
            logging.info("Connecting...")
            try:
                self._ws = yield tornado.websocket.websocket_connect(self._url)
            except:
                logging.error("Connection Failed: Error:", exc_info=True)
            else:
                logging.info("Connected.")
        return 0


if __name__ == '__main__':
    o = VehicleAPI("ws://192.168.12.250/ws")
    o.start()
    print(o.ping())
