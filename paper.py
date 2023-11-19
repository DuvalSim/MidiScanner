import cv2
import os

from midi_scanner.utils.preprocessing import get_lower_image
import imutils as imutils
import numpy as np
from git_utils import preprocessing, key_detection

from skimage.metrics import structural_similarity as compare_ssim

from midi_scanner.utils.key_detection import get_black_keys, get_white_keys

images_dir = "media"
base_img_name = "FirstFrame.png"

base_img = cv2.imread(os.path.join(images_dir, "cropped.png"))


# Open the video file
cap = cv2.VideoCapture('./media/FFX.mp4')

# Check if the video file was successfully opened
if not cap.isOpened():
	print('Error opening video file')

totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

ret, first_frame = cap.read()

first_frame = first_frame[290: first_frame.shape[0] - 3, :,:]

white_notes = get_white_keys(clean_frame=first_frame)
black_notes = get_black_keys(clean_frame=first_frame)

fps = cap.get(cv2.CAP_PROP_FPS)

cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 73) + 15)
ret, test_frame = cap.read()

test_frame = test_frame[290: test_frame.shape[0] - 3, :,:]

print("black notes:",black_notes)

def get_cropped(img):
	img = img[200: 210, :,:]
	return img

# first_frame = get_cropped(first_frame)
#
# fps = cap.get(cv2.CAP_PROP_FPS)
#
# cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 73) + 15)
# ret, test_frame = cap.read()
#
# test_frame = get_cropped(test_frame)

cv2.waitKey(0)

grayA = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
grayB = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)

diff = cv2.absdiff(grayA, grayB)

diff_bot, diff_top = get_lower_image(diff)

cv2.destroyAllWindows()

thresh_bot = cv2.threshold(diff_bot, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]	
thresh_top = cv2.threshold(diff_top, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

key_pressed_image = first_frame.copy()

for note in white_notes:

	 
	print(f"Note {note.note} : {note.start_x} - {note.end_x} - {np.mean(thresh_bot[:,note.start_x:note.end_x] / 255)}")
	if np.mean(thresh_bot[:,note.start_x:note.end_x] / 255) > 0.4:
		print("is pressed:", note.note)
		key_pressed_image = cv2.rectangle(key_pressed_image, (note.start_x, key_pressed_image.shape[0] - thresh_bot.shape[0]),(note.end_x,key_pressed_image.shape[0]) , (255, 0, 0), 1)



cv2.imshow("white key pressed", key_pressed_image)

for note in black_notes:
	print(note)
	print(f"{np.mean(thresh_top[:,note['left']:note['left'] + note['width']] / 255)}")
	if np.mean(thresh_top[:,note["left"]:note["left"] + note["width"]] / 255) > 0.4:
		print("is pressed:", note["note"])
		key_pressed_image = cv2.rectangle(key_pressed_image, (note["left"], 0),( note["left"]+note["width"], note["height"]) , (0, 0, 255), 1)

cv2.imshow("Black key pressed", key_pressed_image)
# black notes



# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)

# for c in cnts:
# 	# compute the bounding box of the contour and then draw the
# 	# bounding box on both input images to represent where the two
# 	# images differ
# 	(x, y, w, h) = cv2.boundingRect(c)
# 	cv2.rectangle(first_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
# 	cv2.rectangle(test_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
# show the output images
cv2.imshow("Original", first_frame)
cv2.imshow("Modified", test_frame)
cv2.waitKey(0)

#
# # Loop through each frame in the video
# while True:
#     # Read the next frame from the video
#     ret, frame = video.read()
#
#     # Check if the frame was successfully read
#     if not ret:
#         break
#
#     # Process the frame here (e.g. display it)
#     cv2.imshow('frame', frame)
#
#     # Wait for a key press to exit
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         break

# Release the video capture object and close all windows
cap.release()
