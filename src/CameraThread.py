import logging
import threading
import asyncio

try:
    import numpy as np
    import cv2
except ImportError:
    raise ImportError("OpenCV is not installed, (or make sure you have enabled its python bindings)")

try:
    import tornado.ioloop
    import tornado.gen
    import tornado.websocket
except ImportError:
    raise ImportError("Install tornado, example: #pip3 install tornado")


class CameraThread(threading.Thread):

    def __init__(self, url, q):
        super(CameraThread, self).__init__(name="CameraThread")
        self._url = url
        self._q = q
        self._evt = threading.Event()
        self._ws = None

    def _handleStandardFeed(self):
        cap = cv2.VideoCapture()

        logging.info("Waiting for video feed...")
        while not self._evt.isSet() and not cap.isOpened():
            cap.open(self._url)
            self._evt.wait(2)
        logging.info("video feed connected.")

        while not self._evt.isSet():
            try:
                self._q.put(cap.read()[1])
            except:
                logging.error("Exc", exc_info=True)

            self._evt.wait(0.01)
        logging.debug("quit")

    @tornado.gen.coroutine
    def _handleWsFeed(self):
        while self._evt:
            logging.info("Waiting for video feed...")
            try:
                self._ws = yield tornado.websocket.websocket_connect(self._url)
            except:
                logging.error("Connection Failed: Error:", exc_info=True)
            else:
                logging.info("Connected.")
                while not self._evt.isSet():
                    msg = yield self._ws.read_message()
                    if msg is None:
                        logging.error("Received Empty Message")
                        self._ws = None
                        break
                    else:
                        file_bytes = np.asarray(bytearray(msg), dtype=np.uint8)
                        mx = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
                        self._q.put(mx)

    def run(self):
        if str(self._url).startswith("ws://"):
            asyncio.set_event_loop(asyncio.new_event_loop())  # Create an async loop for the current Thread
            self._ws = None
            self._handleWsFeed()
            tornado.ioloop.IOLoop.instance().start()
        else:
            self._handleStandardFeed()
