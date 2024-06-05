import cv2
from enum import Enum
import numpy as np

class ColorFormat(Enum):
        RGB = 1
        BGR = 2
        HEX = 3

class MidiScannerColor:
    
    def __init__(self, color, color_format:ColorFormat):
        
        if color_format == ColorFormat.HEX:
            if isinstance(color, str) and color.startswith('#'):
                self.hex = color
                self.rgb = self.hex_to_rgb(color)
                self.bgr = self.rgb_to_bgr(self.rgb)
            else:
                raise ValueError("String color must be in HEX format starting with '#'")
        else:
            if len(color) == 3:
                color = [round(i) for i in color]
                if color_format == ColorFormat.RGB:
                    self.rgb = color
                    self.bgr = self.rgb_to_bgr(color)
                    self.hex = self.rgb_to_hex(color)
                elif color_format == ColorFormat.BGR:
                    self.bgr = color
                    self.rgb = self.bgr_to_rgb(color)
                    self.hex = self.rgb_to_hex(self.rgb)
                else:
                    raise ValueError("Invalid color format. Use HEX, BGR or RGB tuple.")
            else:
                print(len(color))
                print([isinstance(c, int) for c in color])
                raise ValueError("Tuple color must contain three integers")

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
        return self.bgr

    def get_hex(self):
        return self.hex

# if __name__ == '__main__':
#     # Example usage
#     color = MidiScannerColor('#ff5733', ColorFormat.HEX)
#     print(f"RGB: {color.get_rgb()}")  # Output: RGB: (255, 87, 51)
#     print(f"BGR: {color.get_bgr()}")  # Output: BGR: (51, 87, 255)
#     print(f"HEX: {color.get_hex()}")  # Output: HEX: #ff5733

#     color = MidiScannerColor((255, 87, 51), ColorFormat.BGR)
#     print(f"RGB: {color.get_rgb()}")  # Output: RGB: (255, 87, 51)
#     print(f"BGR: {color.get_bgr()}")  # Output: BGR: (51, 87, 255)
#     print(f"HEX: {color.get_hex()}")  # Output: HEX: #ff5733
