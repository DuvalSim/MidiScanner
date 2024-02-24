import cv2
from midi_scanner.utils import preprocessing as preproc

import logging

CROP_KEYBOARD_WINDOW_NAME = 'Crop keyboard'
CROP_PREVIEW_WINDOW_NAME = 'Preview'
CROP_RESULT_WINDOW_NAME = "Cropped image"

class CroppingWindow():    

    def __init__(self, video_filepath, frame_idx) -> None:
        
        self.logger = logging.getLogger("CroppingWindow")
        video_capture = cv2.VideoCapture(video_filepath)
        video_capture.set(cv2.CAP_PROP_POS_FRAMES,frame_idx)
        _, self.clean_frame = video_capture.read()

        self.logger.debug_image(self.clean_frame, "Title original")

        video_capture.release()

        # self.drawing_frame = self.clean_frame.copy()

        self.drawing = False
        self.top_left_pt, self.bottom_right_pt = (-1, -1), (-1, -1)

        cv2.namedWindow(CROP_KEYBOARD_WINDOW_NAME)
        cv2.setMouseCallback(CROP_KEYBOARD_WINDOW_NAME, self.mouse_callback)


    def mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.top_left_pt = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.bottom_right_pt = (x, y)

            drawing_frame = self.clean_frame.copy()  # Reset img_copy to the original frame
            cv2.rectangle(drawing_frame, self.top_left_pt, self.bottom_right_pt, (0, 255, 0), 2)
            cv2.imshow(CROP_KEYBOARD_WINDOW_NAME, drawing_frame)

            cropped_img = preproc.crop_image(self.clean_frame, self.top_left_pt, self.bottom_right_pt)
            cv2.imshow(CROP_PREVIEW_WINDOW_NAME, cropped_img)
        
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            drawing_frame = self.clean_frame.copy()  # Reset img_copy to the original frame
            cv2.rectangle(drawing_frame, self.top_left_pt, (x, y), (0, 255, 0), 2)
            cv2.imshow(CROP_KEYBOARD_WINDOW_NAME, drawing_frame)
            

    def get_cropped_dimension(self):    

        cv2.imshow(CROP_KEYBOARD_WINDOW_NAME, self.clean_frame)    

        while True:

            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                cropped_image = preproc.crop_image(self.clean_frame, self.top_left_pt, self.bottom_right_pt)
                cv2.imshow(CROP_RESULT_WINDOW_NAME, cropped_image)
                break

            elif key == 27:
                break

        cv2.destroyAllWindows()

        return *self.top_left_pt, *self.bottom_right_pt