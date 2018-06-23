import logging
import threading

try:
    import numpy as np
except ImportError:
    raise ImportError("Numpy is not installed, (#pip install numpy)")

try:
    import cv2
except ImportError:
    raise ImportError("OpenCV is not installed, (or make sure you have enabled its python bindings)")


class CvThread(threading.Thread):

    def __init__(self, q, lowerColorHSV = (0,0,0,0), upperColorHSV=(180,255,35,0), roiEnabled=True):
        super(CvThread, self).__init__(name="CvThread")
        self._q = q  # Frames Queue (Shared with cameraThread)
        self._lowerColorHSV = lowerColorHSV
        self._upperColorHSV = upperColorHSV
        self._roiEnabled = roiEnabled

        self._evt = threading.Event()  # Quit Event
        self._autoPilotEnabled = False

    def _drive(self, data):
        # Override this method with your real car controls
        if data is None:
            logging.info("STOP")
        elif data[0] > 0:
            logging.info("GO LEFT")
        elif data[0] < 0:
            logging.info("GO RIGHT")
        else:
            logging.info("GO FORWARD")

    def run(self):
        while not self._evt.isSet():

            if self._q.empty():  # Wait for frame
                self._evt.wait(0.01)
                continue

            frameBGR = self._q.get()  # Get Frame

            # Extract ROI from frame
            if self._roiEnabled:
                # USE ROI
                yAxis = int(frameBGR.shape[1]/2)
                ROI_OFFSETS = np.array([0, yAxis], int)
                frameROI_BGR = frameBGR[yAxis:frameBGR.shape[1], 0:frameBGR.shape[1]]
            else:
                # DO NOT USE ROI
                ROI_OFFSETS = np.array([0, 0], int)
                frameROI_BGR = frameBGR

            # Blur the frame to reduce noise
            frameROI_BGR = cv2.blur(frameROI_BGR, (22, 22))
            frameROI_HSV = cv2.cvtColor(frameROI_BGR, cv2.COLOR_BGR2HSV)

            # get Black pixels (this values depends on light of your room) and color of your line (in this case BLACK)
            hsv_thresh = cv2.inRange(frameROI_HSV, self._lowerColorHSV, self._upperColorHSV)
            hsv_thresh = cv2.morphologyEx(hsv_thresh, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))  # Fill (small) holes

            # Detect countours
            _, hsv_thresh_contours, _ = cv2.findContours(hsv_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # Take the highest (yAxis) contour (filters out some false positives)
            try:
                bestContour = max(hsv_thresh_contours, key=lambda p: cv2.boundingRect(p)[3])
            except:
                bestContour = None

            centerOfFrame = np.array([frameBGR.shape[1] / 2, frameBGR.shape[0] / 2], int)

            try:
                if bestContour is not None:
                    cv2.putText(frameBGR, "Line: FOUND", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    bestContour += ROI_OFFSETS
                    cv2.drawContours(frameBGR, bestContour, -1, (0, 255, 0), 2)

                    wqd = tuple(bestContour[bestContour[:, :, 1].argmin()][0])  # Most external Top point
                    cv2.circle(frameBGR, wqd, 7, (255, 255, 255), -1)
                    extTop = np.array([wqd[0], wqd[1]], int)

                    # df is the distance (px) between the center of the frame (center of car) and the most external top point of the line
                    # df[0] -> X axis distance
                    # df[1] -> Y axis distance
                    df = centerOfFrame - extTop
                    if self._autoPilotEnabled:
                        self._drive(df)
                else:
                    cv2.putText(frameBGR, "Line: NOT FOUND", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    if self._autoPilotEnabled:
                        self._drive(None)

            except Exception:
                logging.error("Exc", exc_info=True)

            # UI: Draw xAxis median line && Center of Frame
            cv2.circle(frameBGR, (centerOfFrame[0], centerOfFrame[1]), 7, (255, 255, 255), -1)
            cv2.line(frameBGR, (centerOfFrame[0], 0), (centerOfFrame[0], frameBGR.shape[0]),
                     (0, 255, 255), 2)

            if self._autoPilotEnabled:
                cv2.putText(frameBGR, "AutoPilot: ON", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(frameBGR, "AutoPilot: OFF", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow('frame', frameBGR)
            self._q.task_done()

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q") or k == 27:  # Q or ESC -> close
                self._evt.set()
                break

            elif k == ord(" "):  # Spacebar toggles AutoPilot
                self._autoPilotEnabled = not self._autoPilotEnabled
                if not self._autoPilotEnabled:  # if we have just disabled the autopilot STOP the car
                    self._drive(None)

        cv2.destroyAllWindows()
        logging.debug("quit")
        return 0
