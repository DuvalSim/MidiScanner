import cv2
import numpy as np

class ImageProcessor:

    BLACK_WHITE_LIMIT_MARGIN = 2


    # ROI is expected to be (top_left_x, top_left_y, bottom_left_x, bottom_left_y)
    def __init__(self, keyboard_roi, bottom_ratio = 3, top_start_ratio = 5, top_end_ratio =2.5):


        self.bottom_ratio = bottom_ratio
        self.keyboard_region_y = (keyboard_roi[1],keyboard_roi[3])
        self.keyboard_region_x = (keyboard_roi[0],keyboard_roi[2])
        self.top_start_ratio = top_start_ratio
        self.top_end_ratio = top_end_ratio

        self.black_white_limit = -1

        self.initialized = True

    def set_black_white_limit(self, black_white_limit : int) -> int:
        self.black_white_limit = black_white_limit

    # returns the height of the limit, None if no limit was found
    
    def calculate_and_set_black_white_limit(self, keyboard_image) -> int:
        """
        This is a test
        """

        keyboard_image_gray = cv2.cvtColor(keyboard_image, cv2.COLOR_BGR2GRAY)

        keyboard_image_binary = cv2.threshold(keyboard_image_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        keyboard_image_canny = cv2.Canny(keyboard_image_binary, threshold1=120, threshold2=200)


        # Get lines between 0 and pi  
        lines_canny = cv2.HoughLines(keyboard_image_canny, rho=1, theta=np.pi / 24, threshold=(keyboard_image.shape[1]//5), min_theta=0, max_theta= np.pi )
               
        if lines_canny is None:
            return -1

        # get horizontal lines (pi/2)
        lines_height = [line[0][0] for line in lines_canny if round(float(line[0][1]), 3) == round(np.pi/2,3)]
        lines_height.sort()

        # return the first value that is higher than the middle of the image 
        self.black_white_limit = int([height for height in lines_height if (height > (keyboard_image.shape[0] - keyboard_image.shape[0]/ 2))][0])
        self.black_white_limit += ImageProcessor.BLACK_WHITE_LIMIT_MARGIN

        return self.black_white_limit

    def get_keyboard_image(self, image):
        if self.keyboard_region_x is None:     
            result_image = image[self.keyboard_region_y[0]: self.keyboard_region_y[1],:,:].copy()
        else:
            result_image = image[self.keyboard_region_y[0]: self.keyboard_region_y[1], self.keyboard_region_x[0]: self.keyboard_region_x[1],:].copy()

        return result_image


    def get_white_black_roi(self, image):
        im_height = image.shape[0]

        im_bottom = image[int(im_height - (im_height / self.bottom_ratio)):im_height, :]

        im_top = image[int(im_height/self.top_start_ratio):int(im_height - (im_height / self.top_end_ratio)), :]
        return im_bottom, im_top
    
    def __str__(self) -> str:
        return f"ROI : {self.keyboard_region_x}{self.keyboard_region_y} - limit: {self.black_white_limit}"
