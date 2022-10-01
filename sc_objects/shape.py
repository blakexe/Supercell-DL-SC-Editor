from sc_objects.sc_object import ScObject
from sc_objects.shape_chunk import ShapeChunk
from utils.reader import Reader
from utils.writer import Writer
from math import ceil
import PIL
from PIL import Image

class Shape(ScObject):
    def __init__(self, main_sc, data, data_type: int):
        ScObject.__init__(self, main_sc, data, data_type)
        self.chunks = []

    def round_school(self, x):
        i, f = divmod(x, 1)
        return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))

    def parse_data(self):
        reader = Reader(self.data, 'little')

        self.shape_id = reader.readInt16()

        reader.i += 4

        while True:
            chunk_type = None
            length = None
            while True:
                chunk_type = reader.readByte()
                length = reader.readInt32()
                if chunk_type in (17, 22):
                    shape_chunk = ShapeChunk(self.main_sc, reader.read(length))
                    shape_chunk.chunk_id = len(self.chunks)
                    shape_chunk.shape_id = self.shape_id
                    shape_chunk.chunk_type = chunk_type
                    shape_chunk.parse_data()
                    self.chunks.append(shape_chunk)
                else:
                    break
            if chunk_type == 0:
                break
            print(f"Unmanaged Chunk Type: {chunk_type}")
            reader.read(length)

    def bounding_box(points):
        x_coordinates, y_coordinates = zip(*points)

        return [(min(x_coordinates), max(y_coordinates)), (max(x_coordinates), min(y_coordinates))] #Top left corner, Bottom right corner

    def render(self) -> bytes:
        shape_left = 0
        shape_top = 0
        shape_right = 0
        shape_bottom = 0
        for chunk in self.chunks:
            shape_left = min(shape_left, min(point[0] for point in chunk.xy_points))
            shape_right = max(shape_right, max(point[0] for point in chunk.xy_points))
            shape_top = min(shape_top, min(point[1] for point in chunk.xy_points))
            shape_bottom = max(shape_bottom, max(point[1] for point in chunk.xy_points))

        width, height = shape_right - shape_left, shape_bottom - shape_top
        size = self.round_school(width), self.round_school(height)

        image = Image.new('RGBA', size)

        chunk: ShapeChunk
        for chunk in self.chunks:
            rendered_region = chunk.render()

            left = min(point[0] for point in chunk.xy_points)
            top = min(point[1] for point in chunk.xy_points)

            if chunk.xy_points[0][0] - chunk.xy_points[1][0] > 0:
                #Mirror x
                rendered_region = rendered_region.transpose(PIL.Image.FLIP_LEFT_RIGHT)

            x = self.round_school(left + abs(shape_left))
            y = self.round_school(top + abs(shape_top))

            image.paste(rendered_region, (x, y), rendered_region)

        return image


    # def export(self) -> bytes:
    #     writer = Writer('little')

    #     writer.writeInt16(self.shape_id)

    #     writer.writeInt16(0) #2 unused bytes
    #     writer.writeInt16(0) #2 unused bytes

    #     for chunk in self.chunks:
    #         writer.writeByte(chunk.chunk_type) #chunk type

    #         exported = chunk.export()

    #         writer.writeInt32(len(exported)) # length
    #         writer.write(exported) #data
        

    #     writer.writeUInt(0) #1
    #     writer.writeInt32(0) #4

    #     return writer.buffer
