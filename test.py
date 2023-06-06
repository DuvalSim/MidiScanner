import cv2
import os
from utils import preprocessing, key_detection

images_dir = "media"
base_img_name = "FirstFrame.png"

base_img = cv2.imread(os.path.join(images_dir, base_img_name))
cv2.imshow("test", base_img)

cv2.waitKey(0)

binary_rectified_sobel, binary_rectified = preprocessing.getBinaryImages(base_img)

whiteKeys, numWhiteKeys, white_notes = key_detection.detect_white_keys(binary_rectified_sobel, "A3")

print(whiteKeys)
print(numWhiteKeys)
print(white_notes)

cv2.waitKey(0)

# closing all open windows
cv2.destroyAllWindows()

