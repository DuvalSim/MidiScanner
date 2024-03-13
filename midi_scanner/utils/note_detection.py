import cv2


def get_frame_diff(frame_1, frame_2):
	grayA = cv2.cvtColor(frame_1, cv2.COLOR_BGR2GRAY)
	grayB = cv2.cvtColor(frame_2, cv2.COLOR_BGR2GRAY)

	return cv2.absdiff(grayA, grayB)

def record_notes(progress_callback):

	
	return 