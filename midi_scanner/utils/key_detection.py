import cv2
import numpy as np
from midi_scanner.utils.visualization import display_connected_components, display_lines, put_white_notes_on_image
from midi_scanner.Key import Key

blackNoteString = "a0c1d1f1g1a1c2d2f2g2a2c3d3f3g3a3c4d4f4g4a4c5d5f5g5a5c6d6f6g6a6c7d7f7g7a7"
whiteNoteString = "A0B0C1D1E1F1G1A1B1C2D2E2F2G2A2B2C3D3E3F3G3A3B3C4D4E4F4G4A4B4C5D5E5F5G5A5B5C6D6E6F6G6A6B6C7D7E7F7G7A7B7C8"


def _get_keys_from_lines(lines, start_key, img_width):
	note_string = blackNoteString if start_key.lower() == start_key else whiteNoteString
	notes = []
	lines_x = [int(l[0][0]) for l in lines]
	lines_x = np.sort(lines_x).tolist()

	lines_x.insert(0, 0)
	lines_x.append(img_width)

	offset = note_string.find(start_key)

	note_idx = 0

	for i in range(len(lines_x) - 1):
		l_x = lines_x[i]
		l_x_1 = lines_x[i + 1]

		if l_x_1 - l_x > 10:
			current_note = note_string[offset + note_idx * 2: offset + note_idx * 2 + 2]
			note_idx += 1
			notes.append(Key(current_note, start_x=l_x, end_x=l_x_1))

	return notes


def get_black_keys(base_img, start_key="a0"):
	img_grey = cv2.cvtColor(base_img, cv2.COLOR_RGB2GRAY)
	thresh, img_binary = cv2.threshold(img_grey, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

	img_negative = cv2.bitwise_not(img_binary)

	# Erode to remove lines between white keys
	eroded = cv2.erode(img_negative, cv2.getStructuringElement(cv2.MORPH_ERODE, (7, 7)))

	# Perform connected component labeling on the negative image
	num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)

	display_connected_components(num_labels, labels, stats, centroids, blackNoteString)
	offset = blackNoteString.find(start_key)

	# TODO
	# remove small regions

	black_keys = []
	for label in range(1, num_labels):  # skip background
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

	return black_keys


def get_white_keys(clean_frame):
	im_height = clean_frame.shape[0]
	im_bottom = clean_frame[int(im_height - (im_height / 5)):im_height, :]

	gray = cv2.cvtColor(im_bottom, cv2.COLOR_BGR2GRAY)

	canny_binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	canny_binary = cv2.Canny(canny_binary, threshold1=120, threshold2=200)

	cv2.imshow("canny_binary", canny_binary)

	# Get lines with theta = 0 (vertical lines)
	lines_canny = cv2.HoughLines(canny_binary, rho=1, theta=np.pi / 180, threshold=10, min_theta=0, max_theta=np.pi / 180)

	display_lines("canny_lines", clean_frame, lines_canny)

	white_notes = _get_keys_from_lines(lines_canny, "A0", im_bottom.shape[1])

	white_notes_img = put_white_notes_on_image(base_image=clean_frame.copy(), notes=white_notes)

	cv2.imshow("notes", white_notes_img)
	cv2.waitKey(0)
	return white_notes
