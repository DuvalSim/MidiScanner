import cv2
from enum import Enum
import numpy as np
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
import skimage

class ColorFormat(Enum):
        RGB = 1
        BGR = 2
        HEX = 3
        LAB = 4



class MidiScannerColor:
    
    def __init__(self, color, color_format:ColorFormat):

        self.bgr = None
        self.hex = None
        self.lab = None
        
        if color_format == ColorFormat.HEX:
            if isinstance(color, str) and color.startswith('#'):
                self.hex = color
                self.rgb = self.hex_to_rgb(color)
            else:
                raise ValueError("String color must be in HEX format starting with '#'")
        elif color_format == ColorFormat.LAB:
            self.lab = color
            self.rgb = self.lab_to_rgb(color)
        else:
            if len(color) == 3:
                color = [round(i) for i in color]
                if color_format == ColorFormat.RGB:
                    self.rgb = color
                elif color_format == ColorFormat.BGR:
                    self.bgr = color
                    self.rgb = self.bgr_to_rgb(color)
                else:
                    raise ValueError("Invalid color format. Use HEX, BGR or RGB tuple.")
            else:
                print(len(color))
                print([isinstance(c, int) for c in color])
                raise ValueError("Tuple color must contain three integers")
            
    def rgb_to_lab(self, rgb):
        return skimage.color.rgb2lab([ c / 255.0 for c in rgb])
    
    def lab_to_rgb(self, lab):
        """
        Convert Lab color values to RGB.
        
        Args:
        - lab (list or np.ndarray): List or array of Lab color value as [L, a, b].
        
        Returns:
        - rgb_color (list): List of RGB value as [R, G, B] in the 0-255 range.
        """        
        # Create LabColor object
        lab_color = LabColor(lab[0], lab[1], lab[2])
        
        # Convert Lab to sRGB
        rgb_color = convert_color(lab_color, sRGBColor)
        
        # Ensure the values are in the [0, 255] range and round them
        rgb_color_clamped = [
            max(0, min(255, int(rgb_color.rgb_r * 255))),
            max(0, min(255, int(rgb_color.rgb_g * 255))),
            max(0, min(255, int(rgb_color.rgb_b * 255)))
        ]
        
        return rgb_color_clamped


    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

    def rgb_to_hex(self, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    def rgb_to_bgr(self, rgb_color):
        # Using cv2 to convert RGB to BGR
        rgb_color_np = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2BGR)
        return rgb_color_np[0][0]

    def bgr_to_rgb(self, bgr_color):
        # Using cv2 to convert BGR to RGB
        bgr_color_np = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2RGB)
        return bgr_color_np[0][0]

    def get_rgb(self):
        return self.rgb

    def get_bgr(self):
        if self.bgr is None:
            self.bgr = self.rgb_to_bgr(self.rgb)
        return self.bgr

    def get_hex(self):
        if self.hex is None:
            self.hex = self.rgb_to_hex(self.rgb)
        return self.hex
    
    def get_lab(self):
        if self.lab is None:
            self.lab = self.rgb_to_lab(self.rgb)
        return self.lab
