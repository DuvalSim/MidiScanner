from midi_scanner.utils import ImageProcessor
from midi_scanner.utils.gui_utils import cv2_to_tkinter_image 

import tkinter as tk

import logging

class KeyboardBlacWhiteLimitWindow(tk.Frame):
    """
    Allows user to modify the keyboard black white limit
    Image processor ROI must be initialized
    """
    LIMIT_MARGIN = 5
    PADDING = 0

    def __init__(self, parent, frame_to_display, image_processor: ImageProcessor) -> None:

        tk.Frame.__init__(self, parent)
        
        self.logger = logging.getLogger("CroppingWindow")
        
        self.image_processor = image_processor

        self.keyboard_image = self.image_processor.get_keyboard_image(frame_to_display)
            
        self.confirm_button_text = "Use automatic white keys detection" if self.image_processor.black_white_limit_initialized() else "Confirm white key zone"
        if not self.image_processor.black_white_limit_initialized():   
            self.image_processor.set_black_white_limit(self.keyboard_image.shape[0] //2)

            
        self.init_black_white_limit = self.image_processor.get_black_white_limit()

        # Create resources
        keyboard_frame_tk = cv2_to_tkinter_image(self.keyboard_image)
        
        self.img_canvas = tk.Canvas(self, width=keyboard_frame_tk.width() + KeyboardBlacWhiteLimitWindow.PADDING*2 , height=keyboard_frame_tk.height() + KeyboardBlacWhiteLimitWindow.PADDING*2 )
        self.img_canvas.grid(column=0, row=0, columnspan=2)

        # Add the image to the canvas
        self.img_canvas.create_image(KeyboardBlacWhiteLimitWindow.PADDING, KeyboardBlacWhiteLimitWindow.PADDING, anchor=tk.NW, image=keyboard_frame_tk)
        self.img_canvas.image = keyboard_frame_tk


        # Draw the initial horizontal line
        self.black_white_line_id = self.img_canvas.create_line(KeyboardBlacWhiteLimitWindow.PADDING,
                                                                self.image_processor.get_black_white_limit()+ KeyboardBlacWhiteLimitWindow.PADDING,
                                                                  keyboard_frame_tk.width() + KeyboardBlacWhiteLimitWindow.PADDING,
                                                                    self.image_processor.get_black_white_limit()+ KeyboardBlacWhiteLimitWindow.PADDING,
                                                                      fill="blue", width=2)


        self.img_canvas.tag_bind(self.black_white_line_id, "<B1-Motion>", self._on_move_line)
        # self.img_canvas.tag_bind(self.black_white_line_id, "<ButtonRelease-1>", self._on_finish_move)

        
        ## Buttons
        self.confirm_button = tk.Button(self, text=self.confirm_button_text, command=self.destroy)
        self.confirm_button.grid(row=1, column=0, sticky="NSEW", columnspan=1)

        self.reset_button = tk.Button(self, text="Reset to initial region", command=self._reset)
        self.reset_button.grid(row=1, column=1, sticky="NSEW", columnspan=1)

        ## Preview
        self.preview_label = tk.Label(self)
        self.preview_label.grid(column=0, row=2, columnspan=2, sticky="N")

        # init preview
        self._update_line_and_preview()


    def _on_move_line(self, event):
        
        min_y, max_y = (KeyboardBlacWhiteLimitWindow.LIMIT_MARGIN, self.keyboard_image.shape[0] - KeyboardBlacWhiteLimitWindow.LIMIT_MARGIN)

        # Do not move line if outside of bounds
        if event.y <= min_y or event.y >= max_y:
            return
        
        self.confirm_button.configure(text="Confirm white key zone")

        self.image_processor.set_black_white_limit(event.y)
        self._update_line_and_preview()

    def _update_line_and_preview(self):
         # Update line
        new_height = self.image_processor.get_black_white_limit()
        self.img_canvas.moveto(self.black_white_line_id, 0, new_height)

        # Update preview
        preview_image = self._get_current_image_bottom()
        self.preview_label.configure(image=preview_image)
        self.preview_label.image = preview_image


    def _get_current_image_bottom(self):
        bottom_img, _ = self.image_processor.get_bottom_top_keyboard(self.keyboard_image)
        preview_image_tk = cv2_to_tkinter_image(bottom_img)
        return preview_image_tk
    
    def _reset(self):
        self.confirm_button.configure(text=self.confirm_button_text)
        self.image_processor.set_black_white_limit(self.init_black_white_limit)
        self._update_height()

