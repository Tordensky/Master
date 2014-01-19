import numpy
import cv2
import matplotlib.pyplot as plt

if __name__ == "__main__":
    image = cv2.imread("TestImages/coloredBalls.jpg", cv2.IMREAD_COLOR)
    b, g, r = cv2.split(image)
    print b

    imgRGB = cv2.merge([r, g, b])

    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    plt.imshow(imgRGB)
    plt.show()

    cv2.imshow("bgr image", image)
    cv2.imshow("rgb image", imgRGB)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
