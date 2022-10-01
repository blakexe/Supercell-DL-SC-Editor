from sc_objects.sc_object import ScObject
from utils.reader import Reader
from utils.writer import Writer
import numpy as np
from PIL import Image

class Texture(ScObject):
    def __init__(self, main_sc, data: bytes, data_type: int):
        ScObject.__init__(self, main_sc, data, data_type)
        self.parse_data()

    def parse_rgb565(self, reader: Reader) -> bytes:
        self.width = reader.readUInt16()
        self.height = reader.readUInt16()

        pixels = []

        for h in range(self.height):
            column = []
            for w in range(self.width):
                color = reader.readUInt16()

                r = ((color >> 11) & 0x1F) << 3
                g = ((color >> 5) & 0x3F) << 2
                b = (color & 0X1F) << 3

                column.append((r, g, b))
            pixels.append(column)

        array = np.array(pixels, dtype=np.uint8)

        self.image = Image.fromarray(array)

    def parse_rgba4444(self, reader: Reader) -> bytes:
        self.width = reader.readUInt16()
        self.height = reader.readUInt16()

        pixels = []

        for h in range(self.height):
            column = []
            for w in range(self.width):
                color = reader.readUInt16()

                r = ((color >> 12) & 0xF) << 4
                g = ((color >> 8) & 0xF) << 4
                b = ((color >> 4) & 0xF) << 4
                a = (color & 0xF) << 4
                column.append((r, g, b, a))
            pixels.append(column)

        array = np.array(pixels, dtype=np.uint8)

        self.image = Image.fromarray(array)

    def parse_rgba8888(self, reader: Reader) -> bytes:
        self.width = reader.readUInt16()
        self.height = reader.readUInt16()

        pixels = []

        for h in range(self.height):
            column = []
            for w in range(self.width):
                r = reader.readByte()
                g = reader.readByte()
                b = reader.readByte()
                a = reader.readByte()
                column.append((r, g, b, a))
            pixels.append(column)

        array = np.array(pixels, dtype=np.uint8)

        self.image = Image.fromarray(array)

    def parse_data(self):
        reader = Reader(self.data, "little")
        im_type = reader.readByte()

        if im_type == 0:
            self.parse_rgba8888(reader)
        elif im_type == 2:
            self.parse_rgba4444(reader)
        elif im_type == 4:
            self.parse_rgb565(reader)
    
    def export(self) -> bytes:
        writer = Writer("little")

        writer.writeUByte(0)

        writer.writeUInt16(self.image.width)
        writer.writeUInt16(self.image.height)

        self.image = self.image.convert("RGBA")

        writer.buffer += np.array(self.image).tobytes()
        
        return writer.buffer

    def render(self) -> Image:
        return self.image