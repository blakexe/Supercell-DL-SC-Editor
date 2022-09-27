from contextlib import nullcontext
from sc_objects.sc_object import ScObject
from sc_objects.shape_chunk import ShapeChunk
from utils.reader import Reader

class Shape(ScObject):
    def __init__(self, main_sc, data, data_type: int):
        ScObject.__init__(self, main_sc, data, data_type)
        self.chunks = []

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


