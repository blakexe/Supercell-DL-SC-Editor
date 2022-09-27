from sc_objects.sc_object import ScObject
from utils.reader import Reader
from PIL import Image

class ShapeChunk(ScObject):
    def __init__(self, main_sc, data):
        ScObject.__init__(self, main_sc, data, 0)
        self.chunk_type = None
        self.uv_points = []
        self.chunk_id = None
        self.shape_id = None


    def parse_data(self):
        reader = Reader(self.data, 'little')

        self.texture_id = reader.readByte()
        shape_point_count = reader.readByte()
        texture = self.main_sc.textures[self.texture_id]

        print("\n\n")
        for i in range(shape_point_count):
            x = reader.readInt32() * 0.05
            y = reader.readInt32() * 0.05
            self.uv_points.append((x, y))
            print(f"x: {x}, y: {y}")
        if self.chunk_type == 22:
            for i in range(shape_point_count):
                u = (reader.readUInt16() / 65535.0) * texture.image.width
                v = (reader.readUInt16() / 65535.0) * texture.image.height
                self.uv_points.append((u, v))
                print(f"u: {u}, v: {v}")
        else:
            for i in range(shape_point_count):
                u = reader.readUInt16()
                v = reader.readUInt16()
                self.uv_points.append((u, v))
                print(f"u: {u}, v: {v}")
        print("\n\n")
                
        
