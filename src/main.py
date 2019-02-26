import time
import queue
import logging

try:
    import numpy as np
    import cv2
except ImportError:
    raise ImportError("OpenCV is not installed, (or make sure you have enabled its python bindings)")

from CameraThread import CameraThread
# from Pilot import Pilot as CvThread
from CvThread import CvThread
from SignalDetector import SignalDetector


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    lst = queue.LifoQueue(5)
    # Video source can be anything compatible with cv2.VideoCapture.open()
    # if source is wsCamera url must start with ws://
    # in DEMO videofeed is provided by a RPI 3B and videoStreamer.py

    # camTh = CameraThread("ws://192.168.12.131:8000/ws", lst)
    camTh = CameraThread("http://192.168.1.244:8080/video", lst)
    # camTh = CameraThread(0, lst)
    camTh.setDaemon(True)
    camTh.start()

    # cvTh = CvThread(lst, (0, 0, 0, 0), (180, 255, 35, 0), True,
    #                [SignalDetector("Stop", cv2.imread("media/TrafficSignals/stop.png", cv2.IMREAD_GRAYSCALE), 12)])
    cvTh = CvThread(lst, (0, 0, 0, 0), (180, 255, 35, 0), True, [])
    cvTh.start()
    logging.debug("quit")


1
if __name__ == "__main__":
    main()
