import cv2
import os
import numpy as np


def get_black_keys(base_img, start_key = "a0"):

    img_grey = cv2.cvtColor(base_img, cv2.COLOR_RGB2GRAY)
    thresh, img_binary = cv2.threshold(img_grey, 127, 255, cv2.THRESH_BINARY)

    img_negative = cv2.bitwise_not(img_binary)

    eroded = cv2.erode(img_negative, cv2.getStructuringElement(cv2.MORPH_ERODE, (7,7)))
    # Perform connected component labeling on the negative image

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)

    blackNoteString = "a0c1d1f1g1a1c2d2f2g2a2c3d3f3g3a3c4d4f4g4a4c5d5f5g5a5c6d6f6g6a6c7d7f7g7a7"
    offset = blackNoteString.find(start_key)

    # remove small regions

    black_keys = []
    for label in range(1, num_labels): # skip background
        left, top, width, height, area = stats[label]
        black_note = blackNoteString[offset + (label - 1) * 2: offset + (label - 1) * 2 + 2]
        black_keys.append({
            "left": left,
            "top": top,
            "width": width,
            "centroid": centroids[label],
            "height": height,
            "note": black_note
        })


def display_notes(image, notes):


    img_notes = cv2.putText(img_notes, black_note, (int(centroid_x), int(centroid_y)),fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255,255,255), thickness=1)

# Visualize the labeled image
labeled_image = colors[labels]
cv2.imshow('Labeled Image', labeled_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imshow("binary", img_binary)

cv2.imshow("notes",img_notes)
cv2.waitKey(0)
cv2.destroyAllWindows()