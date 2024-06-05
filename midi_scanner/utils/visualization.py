import cv2
from midi_scanner import Key
import numpy as np
import colorsys
from midi_scanner.utils.ColorMidiScanner import MidiScannerColor

import logging

def generate_color_array(n):
    color_array = np.ndarray(shape=(n, 3), dtype=np.uint8)
    for i in range(n):
        hue = i / n  # Vary the hue component to evenly distribute colors
        saturation = 0.8  # Fixed saturation value
        value = 0.8  # Fixed value/brightness

        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)

        # Scale RGB values to 0-255 range
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

        color_array[i] = [r, g, b]

    return color_array

def display_lines(win_name, img, lines):
	new_img = img.copy()
	for line in lines:
		rho = int(line[0][0])
		theta = line[0][1]
		if theta != 0:
			print("ATTENTION LES CHAINES")
		else:
			new_img = cv2.line(new_img, (rho, 0), (rho, img.shape[0]), 255, 3)

	cv2.imshow(win_name, new_img)


def display_connected_components(num_labels, labeled_image, stats, centroids, black_note_string):
	#colors = np.random.randint(0, 255, size=(num_labels, 3), dtype=np.uint8)
	colors = generate_color_array(num_labels)
	colors[0] = [0, 0, 0]  # Set the background color to black

	colored_image = colors[labeled_image]

	offset = black_note_string.find("c1")

	img_notes = colored_image.copy()
	for label in range(1, num_labels):
		left, top, width, height, area = stats[label]
		centroid_x, centroid_y = centroids[label]

		black_note = black_note_string[offset + (label - 1) * 2: offset + (label - 1) * 2 + 2]
		img_notes = cv2.putText(img_notes, black_note, (int(centroid_x), int(centroid_y)),
												fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.4, color=(255, 255, 255), thickness=1)

	cv2.imshow('Note img', img_notes)


def put_white_notes_on_image(base_image, notes):
	for note in notes:
		text_point = (int((note.start_x + note.end_x) / 2), base_image.shape[0] - 10)
		base_image = cv2.putText(base_image, note.note, text_point, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5, color=(255, 0, 0), thickness=1)
	return base_image

def display_pressed_keys(base_img, keys, level=logging.DEBUG):
	result_img = base_img.copy()

	for key in keys:
		
		color = (255,0,0) if key.is_black() else (0,0,255)
		result_img = cv2.rectangle(result_img, (key.start_x, base_img.shape[0] - 10),( key.end_x, base_img.shape[0]) ,color, 3)

	logging.getLogger("Visualization").log_image_factory(result_img, "pressed keys", level)

def display_color(color: MidiScannerColor, title : str = "Color", level:int = logging.DEBUG):
	image = np.full((100, 100, 3), color.get_bgr()).astype(np.uint8)
	logging.getLogger("Visualization").log_image_factory(image, title, level)
