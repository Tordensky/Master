import cv2
import signal
import freenect
import numpy as np
import cv2.cv as cv

keep_running = True


class DepthTracker():
    def __init__(self):
        cv2.namedWindow("Depth")
        signal.signal(signal.SIGINT, self.handler)
        cv2.createTrackbar("LEVEL", "Depth", 1000, 2047, self.slider_callback)
        cv2.createTrackbar("RANGE", "Depth", 20, 200, self.slider_callback)

    def slider_callback(self, value):
        pass

    @staticmethod
    def handler(signum, frame):
        """Sets up the kill hadnler, catches SIGINT"""
        global keep_running
        keep_running = False

    def run(self):
        global keep_running
        self.init_dept = self._getDepth()
        while keep_running:
            self.executeFrame()
            cv2.waitKey(5)

    def executeFrame(self):
        level = cv2.getTrackbarPos('LEVEL', 'Depth')
        range = cv2.getTrackbarPos('RANGE', 'Depth')

        self._getDepthThreshold(level - range, level)

    def _getDepth(self):
        return  freenect.sync_get_depth(0, freenect.DEPTH_MM)[0]

    def _getDepthThreshold(self, lower, upper):
        depth, timestamp = freenect.sync_get_depth()

        depth = np.subtract(depth, self.init_dept)

        depth = 255 * np.logical_and(depth > lower, depth < upper)
        depth = depth.astype(np.uint8)
        image = cv.CreateImageHeader((depth.shape[1], depth.shape[0]),
                                     cv.IPL_DEPTH_8U,
                                     1)
        cv.SetData(image, depth.tostring(),
                   depth.dtype.itemsize * depth.shape[1])
        cv.ShowImage('Depth', image)



if __name__ == "__main__":
    dpTracker = DepthTracker()
    dpTracker.run()