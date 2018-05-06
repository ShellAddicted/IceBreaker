import time
import threading
import queue
import logging

import cv2

class CameraThread(threading.Thread):

	def __init__(self, url, q):
		super(CameraThread,self).__init__(name="CameraThread")
		self._url = url
		self._evt = threading.Event()
		self._q = q

	def run(self):
		cap = cv2.VideoCapture()
		logging.info("Waiting for video feed...")
		while not self._evt.isSet() and not cap.isOpened():
			cap.open(self._url)
			self._evt.wait(2)
		logging.info("video feed connected.")

		while not self._evt.isSet():
			try:
				_, frameBGR = cap.read()
				self._q.put(frameBGR)
			except:
				logging.error("Exc", exc_info=True)
			self._evt.wait(0.01)
		logging.debug("quit")
		return 0