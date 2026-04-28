import cv2
import numpy as np

def compare_images(img1_path, img2_path):

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    img1 = cv2.resize(img1, (256, 256))
    img2 = cv2.resize(img2, (256, 256))

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray1, gray2)

    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    change_ratio = np.sum(thresh > 0) / (256 * 256)

    return change_ratio


def get_drone_status(change_ratio):

    if change_ratio > 0.15:
        return "HIGH"
    elif change_ratio > 0.05:
        return "MEDIUM"
    else:
        return "LOW"