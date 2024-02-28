# import logging
# import cv2
# import numpy as np
# import logging

# class ImageLogger(logging.Logger):

#     def _display_image_permanent(self, image, title):
#         cv2.imshow(title, image)
#         cv2.waitKey(0)

#     def _display_image_temp(self, image, title):
#         cv2.imshow(image, title)
#         cv2.waitKey(0)
#         cv2.destroyWindow(title)

#     def display_debug_image(self, image, title='Debug Image'):
#         if self.isEnabledFor(logging.DEBUG):
#             self._display_image(image, title)

#     def display_info_image(self, image, title='Info Image'):
#         if self.isEnabledFor(logging.INFO):
#             self._display_image(image, title)

#     def display_warning_image(self, image, title='Warning Image'):
#         if self.isEnabledFor(logging.WARNING):
#             self._display_image(image, title)

#     def display_error_image(self, image, title='Error Image'):
#         if self.isEnabledFor(logging.ERROR):
#             self._display_image(image, title)

# # Example usage:
# if __name__ == "__main__":
#     # Set up the custom logger
#     logger = ImageLogger('MyImageLogger')

#     # Example log messages
#     logger.debug('This is a debug message')
#     logger.info('This is an info message')
#     logger.warning('This is a warning message')
#     logger.error('This is an error message')

#     # Example displaying OpenCV images at different levels
#     debug_image = np.zeros((100, 100), dtype=np.uint8)
#     info_image = np.ones((100, 100), dtype=np.uint8) * 255
#     warning_image = cv2.cvtColor(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8), cv2.COLOR_BGR2RGB)
#     error_image = cv2.putText(np.zeros((100, 100, 3), dtype=np.uint8), 'Error!', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#     logger.display_debug_image(debug_image, title='Debug Image')
#     logger.display_info_image(info_image, title='Info Image')
#     logger.display_warning_image(warning_image, title='Warning Image')
#     logger.display_error_image(error_image, title='Error Image')

import logging
import cv2
import numpy as np
import logging

import logging
import cv2

def find_handler(logger):
    """
    Traverse the logger hierarchy upwards until a logger with handlers is found.
    """
    while logger:
        if logger.handlers:
            return logger.handlers[0]  # Return the first handler found
        logger = logger.parent
    return None

def show_image(self:logging.Logger, image, title, level):
    if self.isEnabledFor(level):
        pathname, lineno, funcname, _ = self.findCaller()  # Get caller information
        record = self.makeRecord(
            self.name, level, pathname, lineno, title, (), None, funcname)  # Pass caller info to makeRecord
        handler = find_handler(self)
        if handler:
            formatted_title = handler.formatter.format(record)  # Using the formatter to format the title
            cv2.imshow(formatted_title, image)
        else:
            self.warning(f"Could not find a suitable handler -- cannot log image [{title}]")

def debug_image(self, image, title='Debug Image'):
    show_image(self, image, title, logging.DEBUG)

def info_image(self, image, title='Info Image'):
    show_image(self, image, title, logging.INFO)

def warning_image(self, image, title='Warning Image'):
    show_image(self, image, title, logging.WARNING)

def error_image(self, image, title='Error Image'):
    show_image(self, image, title, logging.ERROR)

def log_image_factory(self, image, title, level):
    
    if level == logging.INFO:
        self.info_image(image, title)
    elif level == logging.WARNING:
        self.warning_image(image, title)
    elif level == logging.ERROR:
        self.error_image(image, title)
    elif level == logging.DEBUG:
        self.debug_image(image, title)
    else:
        raise ValueError(f"[{level}] is not handled yet")

def setup_image_logger(level):
    logging.basicConfig(level=level)

    logging.Logger.debug_image = debug_image
    logging.Logger.info_image = info_image
    logging.Logger.warning_image = warning_image
    logging.Logger.error_image = error_image
    logging.Logger.log_image_factory = log_image_factory



