import logging
import cv2
import numpy as np
import logging

class ImageLogger(logging.Logger):
    def __init__(self, name, level=logging.DEBUG):
        super().__init__(name, level)

        self.setLevel(level)
        # Create a console handler with a formatter
        # ch = logging.StreamHandler()
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # ch.setFormatter(formatter)
        # self.addHandler(ch)

    def _display_image_permanent(self, image, title):
        cv2.imshow(title, image)
        cv2.waitKey(0)

    def _display_image_temp(self, image, title, level):
        cv2.imshow(image, title)
        cv2.waitKey(0)
        cv2.destroyWindow(title)

    def display_debug_image(self, image, title='Debug Image'):
        if self.isEnabledFor(logging.DEBUG):
            self._display_image(image, title)

    def display_info_image(self, image, title='Info Image'):
        if self.isEnabledFor(logging.INFO):
            self._display_image(image, title)

    def display_warning_image(self, image, title='Warning Image'):
        if self.isEnabledFor(logging.WARNING):
            self._display_image(image, title)

    def display_error_image(self, image, title='Error Image'):
        if self.isEnabledFor(logging.ERROR):
            self._display_image(image, title)

# Example usage:
if __name__ == "__main__":
    # Set up the custom logger
    logger = ImageLogger('MyImageLogger')

    # Example log messages
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')

    # Example displaying OpenCV images at different levels
    debug_image = np.zeros((100, 100), dtype=np.uint8)
    info_image = np.ones((100, 100), dtype=np.uint8) * 255
    warning_image = cv2.cvtColor(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8), cv2.COLOR_BGR2RGB)
    error_image = cv2.putText(np.zeros((100, 100, 3), dtype=np.uint8), 'Error!', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    logger.display_debug_image(debug_image, title='Debug Image')
    logger.display_info_image(info_image, title='Info Image')
    logger.display_warning_image(warning_image, title='Warning Image')
    logger.display_error_image(error_image, title='Error Image')
