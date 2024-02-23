import cv2

class ImageProcessor:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance



    def __init__(self, keyboard_region_y=None, keyboard_region_x = None, bottom_ratio = 3, top_start_ratio = 5, top_end_ratio =2.5):
        if not hasattr(self, 'initialized'):
            
            self.bottom_ratio = bottom_ratio
            self.keyboard_region_y = keyboard_region_y
            self.keyboard_region_x = keyboard_region_x
            self.top_start_ratio = top_start_ratio
            self.top_end_ratio = top_end_ratio

            self.initialized = True

        elif keyboard_region_y is not None:
             raise ValueError("ImageProcessor already initialized - argument keyboard_region must not be set")


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
