import cv2
import numpy as np
import logging

from midi_scanner.utils.visualization import display_lines

class ImageProcessor:

    BLACK_WHITE_LIMIT_MARGIN = 2
    TOP_KEYBOARD_MARGIN = 5
    BOTTOM_KEYBOARD_MARGIN = 2
    BOTTOM_KEYBOARD_MAX = 5

    
    def __init__(self):
        self.logger = logging.getLogger("ImageProcessor")
        self.keyboard_region_y = (-1,-1)
        self.keyboard_region_x = (-1,-1)

        self.black_white_limit = -1

    def keyboard_limits_initialized(self):
        return (self.keyboard_region_x[0] != -1  and self.keyboard_region_x[1] != -1 and self.keyboard_region_y[0] != 1 and self.keyboard_region_y[1] != -1 )

    def black_white_limit_initialized(self):
        return self.black_white_limit != -1
        

    def init_manually(self, keyboard_roi, black_white_limit = -1):
        """
        Keyboard ROI is (x1, y1, x2, y2)
        """
        self.keyboard_region_y = (keyboard_roi[1],keyboard_roi[3])
        self.keyboard_region_x = (keyboard_roi[0],keyboard_roi[2])
        self.black_white_limit = black_white_limit

    def init_from_image(self, image):
        self.set_keyboard_roi_from_image(image)
        self.set_black_white_limit_from_image(image)
    
    def set_black_white_limit_from_image(self, image):
        if not self.keyboard_limits_initialized():
            self.logger.info("Cannot init black white limit because roi not initialized")
            return
        
        keyboard_image = self.get_keyboard_image(image)
        lines_height = self._get_horizontal_lines(keyboard_image)
        
        if lines_height is None:
            self.logger.info("Was not able to find suitable white key zone")
            self.black_white_limit = -1
            return
        
        # Only keep lines below middle of image
        lines_height = [height for height in lines_height if (height > keyboard_image.shape[0]// 2)]

        if len(lines_height) > 0:
            self.black_white_limit = lines_height[0] + ImageProcessor.BLACK_WHITE_LIMIT_MARGIN
        else:
            self.logger.info("Was not able to find suitable white key zone (all lines are above half of the image)")
            self.black_white_limit = -1


    def set_keyboard_roi_from_image(self, image):

        """
        Automatically calculates keyboard ROI from image
        """
        
        lines_height = ImageProcessor._get_horizontal_lines(image)

        if lines_height is None:
            return
        
        # Only take lines that are lower than half of the image

        lines_height = [height for height in lines_height if (height > image.shape[0]/ 2)]

        if len(lines_height) >= 1:            
        
            keyboard_upper_limit = lines_height.pop(0) + ImageProcessor.TOP_KEYBOARD_MARGIN

            if (len(lines_height) == 0) or (lines_height[-1] < (image.shape[0] - ImageProcessor.BOTTOM_KEYBOARD_MAX)):
                keyboard_lower_limit = image.shape[0] - ImageProcessor.BOTTOM_KEYBOARD_MAX
            else:
                keyboard_lower_limit = lines_height.pop()

            self.keyboard_region_x = (0, image.shape[1])
            self.keyboard_region_y = (keyboard_upper_limit, keyboard_lower_limit)
        
        

    def get_black_white_limit(self) -> int:
        return self.black_white_limit

    def set_upper_keyboard_limit(self, y):
        self.keyboard_region_y[0] = y
    
    def set_lower_keyboard_limit(self, y):
        self.keyboard_region_y[1] = y

    def set_left_keyboard_limit(self, x):
        self.keyboard_region_x[0] = x
    
    def set_right_keyboard_limit(self, x):
        self.keyboard_region_x[1] = x

    def set_black_white_limit(self, black_white_limit : int):
        self.black_white_limit = black_white_limit

    def get_upper_keyboard_limit(self):
        return self.keyboard_region_y[0]
    
    def get_lower_keyboard_limit(self):
        return self.keyboard_region_y[1]

    def get_left_keyboard_limit(self):
        return self.keyboard_region_x[0]
    
    def get_right_keyboard_limit(self):
        return self.keyboard_region_x[1]
    
    def get_keyboard_roi(self):
        return (self.keyboard_region_x[0], self.keyboard_region_y[0], self.keyboard_region_x[1], self.keyboard_region_y[1])    

    def set_keyboard_roi(self, x_top_left: int, y_top_left: int, x_bottom_right: int, y_bottom_right: int):

        self.keyboard_region_x = (x_top_left, x_bottom_right)
        self.keyboard_region_y = (y_top_left, y_bottom_right)

    def get_keyboard_image(self, image):

        if self.keyboard_region_x is None:     
            result_image = image[self.keyboard_region_y[0]: self.keyboard_region_y[1],:,:].copy()
        else:
            result_image = image[self.keyboard_region_y[0]: self.keyboard_region_y[1], self.keyboard_region_x[0]: self.keyboard_region_x[1],:].copy()

        return result_image

    def get_bottom_top_keyboard(self, keyboard_img):

        im_bottom = keyboard_img[self.black_white_limit:,:]
        im_top = keyboard_img[:self.black_white_limit,:]
    
        return im_bottom, im_top

    def __str__(self) -> str:
        return f"ROI : {self.keyboard_region_x}{self.keyboard_region_y} - limit: {self.black_white_limit}"
    

    @staticmethod
    def _get_horizontal_lines(image):
        # First get keyboard roi (first and last lines)
        keyboard_image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        keyboard_image_binary = cv2.threshold(keyboard_image_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        keyboard_image_canny = cv2.Canny(keyboard_image_binary, threshold1=120, threshold2=200)


        # Get lines between 0 and pi  
        lines_canny = cv2.HoughLines(keyboard_image_canny, rho=1, theta=np.pi / 24, threshold=(image.shape[1]//5), min_theta=0, max_theta= np.pi )
               
        if lines_canny is None:
            return None

        # get horizontal lines (pi/2)
        lines_height = [int(line[0][0]) for line in lines_canny if round(float(line[0][1]), 3) == round(np.pi/2,3)]
        lines_height.sort()

        display_lines("ImageProcessor lines", image, lines_canny, level=logging.DEBUG)

        return lines_height
