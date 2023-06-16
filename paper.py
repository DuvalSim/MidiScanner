import cv2
import os
import numpy as np
from utils import preprocessing, key_detection

class Note:

    def __init__(self, note, is_black = False, start_x = None, end_x = None):
        self.start_x = start_x
        self.end_x = end_x
        self.note = note
        self.is_black = is_black


def display_lines(win_name,img, lines):
    new_img = img.copy()
    for line in lines:
        rho = int(line[0][0])
        theta = line[0][1]
        if theta != 0:
            print("ATTENTION LES CHAINES")
        else:
            new_img = cv2.line(new_img, (rho, 0), (rho, img.shape[0]), 255, 3)

    cv2.imshow(win_name, new_img)


def get_white_keys(lines, start_key, img_width):
    white_notes = []
    lines_x = [int(l[0][0]) for l in lines]
    lines_x = np.sort(lines_x).tolist()
    print(lines_x)
    lines_x.insert(0,0)
    lines_x.append(img_width)
    whiteNoteString = "A0B0C1D1E1F1G1A1B1C2D2E2F2G2A2B2C3D3E3F3G3A3B3C4D4E4F4G4A4B4C5D5E5F5G5A5B5C6D6E6F6G6A6B6C7D7E7F7G7A7B7C8"
    offset = whiteNoteString.find(start_key)

    note_idx = 0

    for i in range(len(lines_x) - 1):
        l_x = lines_x[i]
        l_x_1 = lines_x[i+1]

        if l_x_1 - l_x > 10:
            current_note = whiteNoteString[offset + note_idx * 2: offset + note_idx * 2 + 2]
            note_idx += 1
            white_notes.append(Note(current_note, start_x=l_x, end_x=l_x_1))

    return white_notes


images_dir = "media"
base_img_name = "FirstFrame.png"

base_img = cv2.imread(os.path.join(images_dir, "cropped.png"))

imheight = base_img.shape[0]
im_bottom = base_img[int(imheight - (imheight / 5)):imheight, :]

cv2.imshow("bottom_image", im_bottom)

binary_rectified_sobel, binary_rectified = preprocessing.getBinaryImages(im_bottom)
cv2.imshow("binary_sobel", binary_rectified_sobel)

gray = cv2.cvtColor(im_bottom, cv2.COLOR_BGR2GRAY)


thresh, canny_binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
canny_binary = cv2.Canny(canny_binary,threshold1= 120,threshold2=200)

cv2.imshow("canny_binary", canny_binary)

cv2.imshow("binary", binary_rectified)


lines_canny = cv2.HoughLines(canny_binary, rho=1, theta=np.pi/180,threshold=10, min_theta=0, max_theta=np.pi/180)

print(binary_rectified.shape)

display_lines("canny_lines",base_img, lines_canny)

white_notes = get_white_keys(lines_canny, "A0", im_bottom.shape[1])

white_notes_img = base_img.copy()

for note in white_notes:
    white_notes_img = cv2.putText(white_notes_img, note.note, (int((note.start_x + note.end_x) / 2), base_img.shape[0] - 10), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255,0,0), thickness=1)

cv2.imshow("notes", white_notes_img)
cv2.waitKey(0)



#eroded = cv2.dilate(canny, cv2.getStructuringElement(cv2.MORPH_ERODE, (5,5)))

cv2.imshow("sobel", binary_rectified_sobel)
imheight = base_img.shape[0]
im_bottom = binary_rectified_sobel[int(imheight - (imheight / 5)):imheight, :]
#im_botton_canny = canny[int(imheight - (imheight / 5)):imheight, :]
# im_botton_canny = cv2.dilate(im_botton_canny, cv2.getStructuringElement(cv2.MORPH_ERODE, (10,3)))
# im_botton_canny = cv2.erode(im_botton_canny, cv2.getStructuringElement(cv2.MORPH_ERODE, (10,3)))
#lines = cv2.HoughLinesP(im_botton_canny, rho=0.2, theta=np.pi/2, threshold=5, minLineLength=40)
#cv2.imshow("bottom", im_botton_canny)
print(im_bottom.shape[0])
cv2.waitKey(0)
#new_lines = [l[0] for l in lines]



imheight = base_img.shape[0]
im_bottom = base_img[int(imheight - (imheight / 5)):imheight, :]
img_grey = cv2.cvtColor(base_img, cv2.COLOR_RGB2GRAY)
#thresh, img_binary = cv2.threshold(imheight, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh, img_binary = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY)
#https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html


cv2.waitKey(0)

# Apply bitwise NOT operation
img_negative = cv2.bitwise_not(img_binary)





eroded = cv2.erode(img_negative, cv2.getStructuringElement(cv2.MORPH_ERODE, (7,7)))
# Perform connected component labeling on the negative image
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)

# Create a random color map for visualization
colors = np.random.randint(0, 255, size=(num_labels, 3), dtype=np.uint8)
colors[0] = [0, 0, 0]  # Set the background color to black
print(labels)
labeled_image = colors[labels]
cv2.destroyAllWindows()
cv2.imshow('test_label', labeled_image)

cv2.waitKey(0)
whiteNoteString = "A0B0C1D1E1F1G1A1B1C2D2E2F2G2A2B2C3D3E3F3G3A3B3C4D4E4F4G4A4B4C5D5E5F5G5A5B5C6D6E6F6G6A6B6C7D7E7F7G7A7B7C8"
offset = whiteNoteString.find("A3")
white_notes = []
# for i in range(0, whiteKeys.shape[0] * 2, 2):
#     white_notes.append(whiteNoteString[i + offset: i + offset + 2])
blackNoteString = "a0c1d1f1g1a1c2d2f2g2a2c3d3f3g3a3c4d4f4g4a4c5d5f5g5a5c6d6f6g6a6c7d7f7g7a7"
offset = blackNoteString.find("a0")


labeled_image = colors[labels]
img_notes = labeled_image.copy()
for label in range(1, num_labels):
    left, top, width, height, area = stats[label]
    centroid_x, centroid_y = centroids[label]
    print(f"Label: {label}")
    print(f"Bounding Box: ({left}, {top}, {width}, {height})")
    print(f"Area: {area}")
    print(f"Centroid: ({centroid_x}, {centroid_y})")
    print("---------------------")
    black_note = blackNoteString[offset + (label - 1)*2: offset + (label-1)*2 + 2]
    white_notes_img = cv2.putText(white_notes_img, black_note, (int(centroid_x), int(centroid_y)),fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(0,0,255), thickness=1)

# Visualize the labeled image
labeled_image = colors[labels]
cv2.imshow('Labeled Image', labeled_image)

cv2.waitKey(0)


cv2.imshow("notes",white_notes_img)
cv2.waitKey(0)
cv2.destroyAllWindows()