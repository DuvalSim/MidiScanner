import logging
import cv2
import numpy as np
import logging
from midi_scanner.utils.ColorMidiScanner import ColorFormat

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



