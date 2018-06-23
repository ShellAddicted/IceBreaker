import time
import queue
import logging

from CameraThread import CameraThread
from CvThread import CvThread


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    lst = queue.LifoQueue(5)
    # Video source can be anything compatible with cv2.VideoCapture.open()
    # in DEMO videofeed is provided by a RPI 3B and videoStreamer.py
    camTh = CameraThread("http://192.168.12.131:8000/stream.mjpg", lst)
    camTh.start()

    cvTh = CvThread(lst, (0, 0, 0, 0), (180, 255, 35, 0), True)
    cvTh.start()

    while True:
        # Who dies first kills the other
        if not camTh.isAlive():
            cvTh._evt.set()

        if not cvTh.isAlive():
            camTh._evt.set()

        # If everyone is dead, quit mainThread
        if not cvTh.isAlive() and not camTh.isAlive():
            break
        time.sleep(0.1)  # Save a bit of CPU
    logging.debug("quit")


if __name__ == "__main__":
    main()
