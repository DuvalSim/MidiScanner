import cv2
import os

from midi_scanner.utils.preprocessing import get_lower_image
from midi_scanner.utils.visualization import display_pressed_keys
import imutils as imutils
import numpy as np

from midi_scanner.Keyboard import Keyboard

def get_cropped_image(img):
    return img[290: img.shape[0] - 3, :,:].copy()

images_dir = "media"
base_img_name = "FirstFrame.png"


# Open the video file
cap = cv2.VideoCapture('./media/FFX.mp4')

# Check if the video file was successfully opened
if not cap.isOpened():
	print('Error opening video file')

totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

ret, first_frame = cap.read()

first_frame = get_cropped_image(first_frame)

keyboard = Keyboard(first_frame)



fps = cap.get(cv2.CAP_PROP_FPS)

#cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 73) + 15)
#ret, current_frame = cap.read()

#current_frame = get_cropped_image(current_frame)
#keyboard.get_pressed_notes(current_frame=current_frame)

#cv2.imshow("current frame", current_frame)

cv2.waitKey(0)
cv2.destroyAllWindows()
nb_frame = 1


# cap.set(cv2.CAP_PROP_POS_FRAMES,450)
# ret, current_frame = cap.read()

# current_frame = get_cropped_image(current_frame)
# keyboard.get_pressed_keys(current_frame=current_frame)

# cv2.imshow("current frame", current_frame)



while True:
    # Read the next frame from the video
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        break

    # Process the frame here (e.g. display it)
    cropped_frame = get_cropped_image(frame)
    cv2.imshow('Current Frame', frame)

    pressed_keys = keyboard.get_pressed_keys(cropped_frame)
    #print(pressed_keys)
    display_pressed_keys(frame, pressed_keys)
    
    cv2.waitKey(0)
    print(nb_frame)
    nb_frame += 1

    # Wait for a key press to exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

# Release the video capture object and close all windows
cap.release()
