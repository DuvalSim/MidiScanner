import cv2
import os
from utils import preprocessing, key_detection


def get_rect(whiteKeys, i):
    return (int(whiteKeys[i,2]), int(whiteKeys[i,1])), (int(whiteKeys[i,3]), int(whiteKeys[i,0]))
    #return (int(whiteKeys[i, 2]), int(whiteKeys[i, 1])), (int(whiteKeys[i, 3]), 159-32)

images_dir = "media"
base_img_name = "FirstFrame.png"

base_img = cv2.imread(os.path.join(images_dir, base_img_name))


binary_rectified_sobel, binary_rectified = preprocessing.getBinaryImages(base_img)




whiteKeys, numWhiteKeys, white_notes = key_detection.detect_white_keys(binary_rectified_sobel, "A3")


pt1, pt2 = get_rect(whiteKeys, 40)
cv2.rectangle(base_img, pt1, pt2, color=(0,0,255))
pt1, pt2 = get_rect(whiteKeys, 19)
cv2.rectangle(base_img, pt1, pt2, color=(0,0,255))
pt1, pt2 = get_rect(whiteKeys, 4)
cv2.rectangle(base_img, pt1, pt2, color=(0,0,255))

cv2.imshow("keys", base_img)
print("White Keys:")
print(whiteKeys)

cv2.waitKey(0)

# closing all open windows
cv2.destroyAllWindows()

