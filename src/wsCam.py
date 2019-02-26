#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    import tornado.websocket
except ImportError:
    raise ImportError("Install tornado, example: #pip3 install tornado")

class wsCameraThread(threading.Thread):

    def __init__(self, url, q):
        super(wsCameraThread, self).__init__(name="wsCameraThread")
        self.url = url
        self._q = q
        self._evt = True

    def run(self):
        aloop = asyncio.new_event_loop()  # Create an async loop for the current Thread
        asyncio.set_event_loop(aloop)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.ws = None
        self.wsrun()
        self.ioloop.start()

    @tornado.gen.coroutine
    def wsrun(self):
        while self._evt:
            logging.info("Waiting for video feed...")
            try:
                self.ws = yield tornado.websocket.websocket_connect(self.url)
            except:
                logging.error("Connection Failed: Error:", exc_info=True)
            else:
                logging.info("Connected.")
                while True:
                    msg = yield self.ws.read_message()
                    if msg is None:
                        logging.error("Empty")
                        self.ws = None
                        break
                    else:
                        file_bytes = np.asarray(bytearray(msg), dtype=np.uint8)
                        mx = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
                        self._q.put(mx)
        return 0

    def stop(self):
        self._evt = False
