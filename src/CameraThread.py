import logging
import threading

try:
    import cv2
except ImportError:
    raise ImportError("OpenCV is not installed, (or make sure you have enabled its python bindings)")


class CameraThread(threading.Thread):

    def __init__(self, url, q):
        super(CameraThread, self).__init__(name="CameraThread")
        self._url = url
        self._q = q
        self._evt = threading.Event()

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
            except Exception:
                logging.error("Exc", exc_info=True)

            self._evt.wait(0.01)
        logging.debug("quit")
        return 0
