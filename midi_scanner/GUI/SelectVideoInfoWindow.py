import cv2
import tkinter as tk
from PIL import Image, ImageTk
import logging

from typing import List, Tuple

from midi_scanner.utils import postprocessing

from midi_scanner.utils.gui_utils import cv2_to_tkinter_image
from midi_scanner.GUI.FrameSliderWindowBase import FrameSliderWindowBase

from midi_scanner.utils.ColorMidiScanner import MidiScannerColor, ColorFormat

class VideoInfoWindow(FrameSliderWindowBase):

    def __init__(self, parent, video_capture, note_played_list, max_parts = 4) -> None:

        super(VideoInfoWindow, self).__init__(parent, video_capture=video_capture)
        
        num_clusters, b_centroids, w_centroids = postprocessing.get_black_white_color_clusters(note_played_list, max_clusters=max_parts)
        self.parent = parent
        self.max_parts = max_parts
        self.min_parts = 1
        self.nb_parts = num_clusters
        # Init color table
        ### Grey
        default_color = MidiScannerColor("#606060", ColorFormat.HEX)
        self.part_colors = []
        for part_idx in range(self.nb_parts):
            
            part_color_black = b_centroids[part_idx] if b_centroids[part_idx] is not None else default_color
            part_color_white = w_centroids[part_idx] if w_centroids[part_idx] is not None else default_color
            self.part_colors.append([part_color_black, part_color_white])
        
        # fill the rest:
        for part_idx in range(self.nb_parts, max_parts):
            self.part_colors.append([default_color, default_color])
         
        # inherited from parent class
        self.img_label.bind("<Button-1>", self.on_img_click)

        
        info_frame = tk.Frame(self)         
        
        
        
        tk.Label(info_frame, text="Select number of parts and key color for each part:").pack(anchor="w")
        tk.Label(info_frame, text="Use detected color or pick one by selecting a part and click on the frame").pack(anchor="w")


        self.colors_frame = tk.Frame(info_frame)

        self.refresh_colors()
        self.selected_picker = (0,0)
        self.color_pickers_dict[self.selected_picker].config(highlightthickness=1, highlightbackground="black")
        self.color_pickers_dict[self.selected_picker].update()

        self.colors_frame.pack()
        info_frame.pack()
        
        confirm_button = tk.Button(self, text="Confirm")
        confirm_button.pack(side="bottom",fill="x")
        confirm_button.bind("<Button-1>", self.confirm_selection)
        

    def refresh_colors(self):

        for widget in self.colors_frame.grid_slaves():
            # if isinstance(widget, tk.Canvas):
            widget.grid_forget()

        tk.Label(self.colors_frame, text="Black key colors:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Label(self.colors_frame, text="White key colors:").grid(row=2, column=0, padx=10, pady=10, sticky="w")

        tk.Label(self.colors_frame, text="Part:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        for part_idx in range(self.nb_parts):
            tk.Label(self.colors_frame, text=f"{part_idx + 1}").grid(row=0, column=part_idx + 1, padx=10, pady=10)
        
        if self.nb_parts > 1:
            tk.Button(self.colors_frame, text="-", command=self.decrease_nb_parts).grid(row=0, column=self.nb_parts + 1, padx=5)

        if self.nb_parts < self.max_parts:
            tk.Button(self.colors_frame, text="+", command=self.increase_nb_parts).grid(row=0, column=self.nb_parts + 2, padx=5)
        
        self.color_pickers_dict = {}
        for part_idx in range(self.nb_parts):
            for key_type_idx in range(2):
                color_canvas = tk.Canvas(self.colors_frame, width=50, height=50, bg=self.part_colors[part_idx][key_type_idx].get_hex())
                color_canvas.bind("<Button-1>", lambda event, arg=(part_idx,key_type_idx): self.on_color_picker_click(event, arg))
                color_canvas.grid(row=key_type_idx + 1, column=part_idx + 1, padx=5, pady=5)
                self.color_pickers_dict[(part_idx,key_type_idx)] = color_canvas

    def increase_nb_parts(self):
        if self.nb_parts < self.max_parts:
            self.nb_parts += 1
            self.refresh_colors()

    def decrease_nb_parts(self):
        if self.nb_parts > self.min_parts:
            self.nb_parts -= 1
            self.refresh_colors()

    def on_img_click(self, event):
        """Handle mouse click event."""
        x = event.x
        y = event.y
        pixel_value = self.current_frame_cv[y, x]
        print("Pixel value at ({}, {}): {}".format(x, y, pixel_value))
        color = '#%02x%02x%02x' % (pixel_value[2], pixel_value[1], pixel_value[0])

        self.color_pickers_dict[self.selected_picker].config(bg=color)
        self.color_pickers_dict[self.selected_picker].update()

        current_part, current_key_type = self.selected_picker
        self.part_colors[current_part][current_key_type] = MidiScannerColor(color, ColorFormat.HEX)

    def on_color_picker_click(self, event, color_picker_id):
               
       if color_picker_id != self.selected_picker:
            self.color_pickers_dict[self.selected_picker].config(highlightthickness=0)
            self.color_pickers_dict[self.selected_picker].update()
            

            self.color_pickers_dict[color_picker_id].config(highlightthickness=1, highlightbackground="black")
            self.color_pickers_dict[color_picker_id].update()
            
            self.selected_picker = color_picker_id

    def confirm_selection(self, event):
        
        if not any([part_color is None for part_color in self.part_colors[:self.nb_parts]]):
            
            self.destroy()
            self.parent.focus_set()


    def pick_music_info(self) -> Tuple[List[MidiScannerColor], List[MidiScannerColor]]:
        """Return the key colors for each part

        Returns:
            Tuple[List[MidiScannerColor], List[MidiScannerColor]]: List of black key colors for each part, List of white key colors for each part
        """
        self.wait_window()
        part_colors = self.part_colors[:self.nb_parts]
        
        return tuple(zip(*part_colors))

