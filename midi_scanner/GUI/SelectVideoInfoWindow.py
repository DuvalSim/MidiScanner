import cv2
import tkinter as tk
from PIL import Image, ImageTk
import logging

from midi_scanner.utils import postprocessing

from midi_scanner.utils.gui_utils import cv2_to_tkinter_image
from midi_scanner.GUI.FrameSliderWindowBase import FrameSliderWindowBase

class VideoInfoWindow(FrameSliderWindowBase):

    def __init__(self, parent, video_capture, note_played_list) -> None:

        super(VideoInfoWindow, self).__init__(parent, video_capture=video_capture)
        
        self.parent = parent


        num_clusters, b_centroids, w_centroids = postprocessing.get_black_white_color_clusters(note_played_list)

        self.img_label.bind("<Button-1>", self.on_img_click)

        
        info_frame = tk.Frame(self)
           
        self.nb_parts = num_clusters
        self.color_canvas = []
        
        self.part_colors_w = w_centroids
        self.part_colors_b = b_centroids
        
        frame_colors = tk.Frame(info_frame)
        tk.Label(frame_colors, text="Select color for each part:").pack()
            
        for part_idx in range(self.nb_parts):
            current_frame_color = tk.Frame(frame_colors)
            tk.Label(current_frame_color, text=f"Part {part_idx + 1}:").pack()

            color_canvas = tk.Canvas(current_frame_color, width=15, height=10, bg="gray")
            color_canvas.bind("<Button-1>", lambda event, arg=part_idx: self.on_color_picker_click(event, arg))
            color_canvas.pack()

            self.color_canvas.append(color_canvas)

            current_frame_color.pack(side="left")
            

        self.color_canvas[0].configure(highlightthickness=1, highlightbackground="black")
        self.color_canvas[0].update()
        self.selected_picker = 0 

        frame_colors.pack()
        info_frame.pack(side="left")

        
        confirm_button = tk.Button(self, text="Confirm")
        confirm_button.pack(side="left",fill="x")
        confirm_button.bind("<Button-1>", self.confirm_selection)
        


    def on_img_click(self, event):
        """Handle mouse click event."""
        x = event.x
        y = event.y
        pixel_value = self.current_frame_cv[y, x]
        print("Pixel value at ({}, {}): {}".format(x, y, pixel_value))
        color = '#%02x%02x%02x' % (pixel_value[2], pixel_value[1], pixel_value[0])
        self.color_canvas[self.selected_picker].config(bg=color)
        self.color_canvas[self.selected_picker].update()

        self.part_colors[self.selected_picker] = color

    def on_color_picker_click(self, event, color_picker_idx):
        if color_picker_idx != self.selected_picker:
            for i in range(len(self.color_canvas)):
                if i != color_picker_idx:
                    self.color_canvas[i].config(highlightthickness=0)
                else:
                    self.color_canvas[color_picker_idx].config(highlightthickness=1, highlightbackground="black")
                    
                self.color_canvas[i].update()
            
            self.selected_picker = color_picker_idx    
        
    def confirm_selection(self, event):
        
        if not any([part_color is None for part_color in self.part_colors]):
            
            self.destroy()
            self.parent.focus_set()


    def pick_music_info(self):
        self.wait_window()
        part_colors = self.part_colors
        
        return part_colors

