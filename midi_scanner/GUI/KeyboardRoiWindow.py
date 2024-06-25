import cv2
from midi_scanner.utils import preprocessing as preproc
from midi_scanner.utils import ImageProcessor
from midi_scanner.utils.gui_utils import cv2_to_tkinter_image 
from typing import Callable

from typing import Tuple

import tkinter as tk

import logging

import copy

CROP_KEYBOARD_WINDOW_NAME = 'Crop keyboard'
CROP_PREVIEW_WINDOW_NAME = 'Preview'
CROP_RESULT_WINDOW_NAME = "Cropped image"

class KeyboardRoiWindow(tk.Frame):
    """
    Allows user to modify the keyboard ROIs
    Image processor must be initialized
    """

    PADDING = 5

    def __init__(self, parent, frame_to_display, image_processor: ImageProcessor) -> None:

        tk.Frame.__init__(self, parent)
        
        self.logger = logging.getLogger("CroppingWindow")
        
        self.image_processor = image_processor

        self.frame_to_display = frame_to_display

        automated_roi = True

        # if keyboard region not initialized set rectangle to the frame dimensions and black white limit to half the picture
        if not self.image_processor.keyboard_limits_initialized():
            automated_roi = False
            black_white_limit = (self.frame_to_display.shape[0] //2)
            self.image_processor.init_manually((0,0, self.frame_to_display.shape[1], self.frame_to_display.shape[0]), black_white_limit)
            
        self.init_roi = self.image_processor.get_keyboard_roi()

        # Create resources
        complete_frame_tk = cv2_to_tkinter_image(self.frame_to_display)
        
        self.img_canvas = tk.Canvas(self, width=complete_frame_tk.width() + KeyboardRoiWindow.PADDING*2 , height=complete_frame_tk.height() + KeyboardRoiWindow.PADDING*2 )
        self.img_canvas.grid(column=0, row=0, columnspan=2)

        # Add the image to the canvas
        img_id = self.img_canvas.create_image(KeyboardRoiWindow.PADDING, KeyboardRoiWindow.PADDING, anchor=tk.NW, image=complete_frame_tk)
        self.img_canvas.image = complete_frame_tk


        min_x, min_y = self.img_canvas.coords(img_id)
        max_x, max_y = (min_x + complete_frame_tk.width(), min_y + complete_frame_tk.height())

        x1, y1, x2, y2 = self.image_processor.get_keyboard_roi()
        x1 += KeyboardRoiWindow.PADDING
        y1 += KeyboardRoiWindow.PADDING
        x2 += KeyboardRoiWindow.PADDING
        y2 += KeyboardRoiWindow.PADDING
        self.rectangle = ResizableRectangle(self.img_canvas,(x1, y1, x2, y2) , (min_x, min_y, max_x, max_y), on_rectangle_release=self._rectangle_release)


        ## Buttons
        self.confirm_button_init_text = "Use automatically detected keyboard region" if automated_roi else "Confirm manual keyboard region"
        self.confirm_button = tk.Button(self, text=self.confirm_button_init_text, command=self.destroy)
        self.confirm_button.grid(row=1, column=0, sticky="NSEW", columnspan=1)

        #
        self.reset_button = tk.Button(self, text="Reset to initial value", command=self._reset)
        self.reset_button.grid(row=1, column=1, sticky="NSEW", columnspan=1)

        ## Keyboard preview
        self.keyboard_preview_label = tk.Label(self)
        self.keyboard_preview_label.grid(column=0, row=2, columnspan=2, sticky="N")

        self._set_current_keyboard_image()

         
    def _rectangle_release(self, event):
        self._update_roi()

    def _update_roi(self):
        # Update preview
        self.confirm_button.configure(text="Confirm manual keyboard region")
        rect_coords = self.rectangle.get_current_coordinates()
        adjusted_coords = [int(coord - KeyboardRoiWindow.PADDING) for coord in rect_coords]
        self.image_processor.set_keyboard_roi(*adjusted_coords)
        self._set_current_keyboard_image()

    def _set_current_keyboard_image(self):
        keyboard_img = self.image_processor.get_keyboard_image(self.frame_to_display)
        preview_image = cv2_to_tkinter_image(keyboard_img)
        self.keyboard_preview_label.configure(image=preview_image)
        self.keyboard_preview_label.image = preview_image      
    
    def _reset(self):
        self.image_processor.set_keyboard_roi(*self.init_roi)
        self.confirm_button.configure(text=self.confirm_button_init_text)
        self._set_current_keyboard_image()

        rect_coords = self.image_processor.get_keyboard_roi()
        adjusted_coords = [int(coord + KeyboardRoiWindow.PADDING) for coord in rect_coords]
        
        self.rectangle.move_to(adjusted_coords)
        
        
         
class ResizableRectangle:

    HANDLE_TAG = "handle"

    def __init__(self, canvas : tk.Canvas, rect_coords: Tuple[int, int, int, int], limit_coords: Tuple[int, int, int, int], on_rectangle_release: Callable,color : str = "red"):
        self.canvas = canvas
        self.limit_coords = limit_coords
        x1, y1, x2, y2 = rect_coords
        self.current_coords = rect_coords

        self.rectangle = [
            canvas.create_line(x1, y1, x2, y1, fill=color, width=2, tags='edge'),  # top
            canvas.create_line(x2, y1, x2, y2, fill=color, width=2, tags='edge'),  # right
            canvas.create_line(x1, y2, x2, y2, fill=color, width=2, tags='edge'),  # bottom
            canvas.create_line(x1, y1, x1, y2, fill=color, width=2, tags='edge')   # left
        ]

        self.r = 3
        
        self.handles = [
            self.canvas.create_oval(x1 - self.r, y1 -self.r, x1 + self.r, y1 + self.r, tags='handle'),  # top-left
            self.canvas.create_oval(x2 - self.r, y1 -self.r, x2 + self.r, y1 + self.r, tags='handle'),    # top-right
            self.canvas.create_oval(x2 - self.r, y2 -self.r, x2 + self.r, y2 + self.r, tags='handle'),    # bottom-right
            self.canvas.create_oval(x1 - self.r, y2 -self.r, x1 + self.r, y2 + self.r, tags='handle'),    # bottom-left
        ]

        for handle in self.handles:
            self.canvas.tag_bind(handle, "<B1-Motion>", lambda event, handle_id = handle: self._on_handle_move(event, handle_id))
        
        self.canvas.tag_bind('handle', "<ButtonRelease-1>", on_rectangle_release)

        self.canvas.itemconfigure('handle', fill=color)

    def _on_handle_move(self, event, handle_id):
        x1, y1, x2, y2 = self.current_coords
        
        minX, minY, maxX, maxY = self.limit_coords

        #top left
        if handle_id == self.handles[0]: 
            x1, y1 = (event.x, event.y)
        # top right
        elif handle_id == self.handles[1]:
            x2, y1 = (event.x, event.y)
        # bottom right
        elif handle_id == self.handles[2]:
            x2, y2 = (event.x, event.y)
        #bottom left
        elif handle_id == self.handles[3]:
            x1, y2 = (event.x, event.y)
        else:
            raise RuntimeError("This handle id does not exist")
        
        x1 = max(x1, minX)
        x1 = min(x1,  x2 - 5)

        x2 = min(x2, maxX)
        x2 = max(x2, x1 +5)

        y1 = max(y1, minY)
        y1 = min(y1, y2 -5)

        y2 = min(y2, maxY)
        y2 = max(y2, y1 + 5)

        self.move_to((x1, y1, x2, y2))

    def move_to(self, coords: Tuple[int, int, int, int]):
        self.current_coords = coords
        self._update_handles()
        self._update_lines()


    def _update_handles(self):
        x1, y1, x2, y2 = self.current_coords
        handle_coords = [
            (x1, y1),  # top-left
            (x2, y1),  # top-right
            (x2, y2),  # bottom-right
            (x1, y2)   # bottom-left
        ]
        for handle, (x, y) in zip(self.handles, handle_coords):
            self.canvas.coords(handle, x-self.r, y-self.r, x+self.r, y+self.r)

    def _update_lines(self):
        x1, y1, x2, y2 = self.current_coords
        self.canvas.coords(self.rectangle[0], x1, y1, x2, y1)  # top
        self.canvas.coords(self.rectangle[1], x2, y1, x2, y2)  # right
        self.canvas.coords(self.rectangle[2], x2, y2, x1, y2)  # bottom
        self.canvas.coords(self.rectangle[3], x1, y2, x1, y1)  # left

    def get_current_coordinates(self):
        return self.current_coords
