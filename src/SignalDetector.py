import numpy as np
import cv2


class SignalDetector:
    def __init__(self, name, trainImg, minMatches=3):
        self._minMatches = minMatches
        self._trainImgShape = trainImg.shape
        self._name = name
        self.result = None

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self._flann = cv2.FlannBasedMatcher(index_params, search_params)

        self._sift = cv2.xfeatures2d.SIFT_create()
        (self._train_kps, self._train_descs) = self._sift.detectAndCompute(trainImg, None)

    def detect(self, image):
        try:
            self.result = None # Clean Previous result
            (kps, descs) = self._sift.detectAndCompute(image, None)
            matches = self._flann.knnMatch(self._train_descs, descs, k=2)

            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)

            if len(good) >= self._minMatches:
                src_pts = np.float32([self._train_kps[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kps[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

                m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                h, w = self._trainImgShape
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, m)

                self.result = [np.int32(dst)]
                # to draw results use cv2.polylines(image, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
        except:
            pass
