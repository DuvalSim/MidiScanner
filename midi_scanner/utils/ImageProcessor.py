import cv2

class ImageProcessor:


    # ROI is expected to be (top_left_x, top_left_y, bottom_left_x, bottom_left_y)
    def __init__(self, keyboard_roi, bottom_ratio = 3, top_start_ratio = 5, top_end_ratio =2.5):


        self.bottom_ratio = bottom_ratio
        self.keyboard_region_y = (keyboard_roi[1],keyboard_roi[3])
        self.keyboard_region_x = (keyboard_roi[0],keyboard_roi[2])
        self.top_start_ratio = top_start_ratio
        self.top_end_ratio = top_end_ratio

        self.initialized = True


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
