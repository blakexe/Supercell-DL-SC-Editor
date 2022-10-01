from utils.reader import Reader
from utils.writer import Writer

from sc_objects.movieclip import MovieClip
from sc_objects.texture import Texture
from sc_objects.sc_object import ScObject
from sc_objects.shape import Shape

class SC():
    def __init__(self):
        self.movie_clip_info = {}

        self.textures = []
        self.shapes = []
        self.movieclips = []
        self.textfields = []
        self.matrix2x3 = []
        self.colortransforms = []
        self.unknowns = []
    
    def import_sc(self, bytes):
        reader = Reader(bytes, 'little')

        #Metadata
        self.shape_count = reader.readUInt16()
        self.movie_clip_count = reader.readUInt16()
        self.texture_count = reader.readUInt16()
        self.text_field_count = reader.readUInt16()
        self.matrix_2x3_count = reader.readUInt16()
        self.color_transform_count = reader.readUInt16()

        print("shape count: " + str(self.shape_count))
        print("clip count: " + str(self.movie_clip_count))
        print("texture count: " + str(self.texture_count))
        print("text field count: " + str(self.text_field_count))
        print("matrix2x3 count: " + str(self.matrix_2x3_count))
        print("transform count: " + str(self.color_transform_count))

        #5 Unused bytes
        reader.i += 5

        #Get movieclip count (metadata)
        self.export_count = reader.readUInt16()
        print("movieclip metadata count: " + str(self.export_count))
        
        #Get movieclip IDs (metadata)
        for i in range(self.export_count):
            id = reader.readInt16()
            print(id)
            self.movie_clip_info[id] = i

        
        #Pair names with movieclip IDs (metadata)
        for i in range(self.export_count):
            name_length = reader.readUInt8()
            name = reader.readChar(name_length)

            #Find the ID in movie clip info based on its order
            key = next(key for key, value in self.movie_clip_info.items() if value == i)

            self.movie_clip_info[key] = name

            print(f"{key}: {name}")

        #Get actual data
        while True:
            data_type = reader.readByte()
            data_length = reader.readInt32()

            if data_type == 0:
                #EOF

                #Parse movieclips
                # for movieclip in self.movieclips:
                #     movieclip.parse_data()

                return

            #Get next set of data
            data = reader.read(data_length)

            #Check the type of data
            if data_type in (1, 16, 19):
                #Texture
                texture = Texture(self, data, data_type)
                self.textures.append(texture)
            elif data_type in (2, 18):
                #Shape
                shape = Shape(self, data, data_type)
                self.shapes.append(shape)
                shape.parse_data()
            elif data_type in (3, 10, 12, 14):
                #Movieclip
                try:
                    movieclip = MovieClip(self, data, data_type)
                    movieclip.parse_data()
                    self.movieclips.append(movieclip)
                except:
                    print("Skipping movie clip due to error")
                    sc_object = ScObject(self, data, data_type)
                    self.unknowns.append(sc_object)

            # elif data_type in (7, 15, 20):
                #Textfield
                # pass
            # elif data_type == 8:
                #Matrix2x3
                # pass
            # elif data_type == 9:
                #Color transform
                # pass
            # elif data_type == 13:
                #Uhhh dunno yet. Something
                # pass
            else:
                #Unknown type
                sc_object = ScObject(self, data, data_type)
                self.unknowns.append(sc_object)

    def export_sc(self) -> bytes:
        writer = Writer('little')

        writer.writeUInt16(self.shape_count)
        writer.writeUInt16(self.movie_clip_count)
        writer.writeUInt16(self.texture_count)
        writer.writeUInt16(self.text_field_count)
        writer.writeUInt16(self.matrix_2x3_count)
        writer.writeUInt16(self.color_transform_count)

        writer.write(bytes(bytearray(5))) #5 empty bytes

        writer.writeUInt16(self.export_count)

        for key in self.movie_clip_info:
            writer.writeInt16(int(key))

        for value in self.movie_clip_info.values():
            writer.writeUInt8(len(value))
            writer.writeChar(value)

        # writer.writeUInt16(len([movieclip for movieclip in self.movieclips if movieclip.export_name != None]))

        # for movieclip in self.movieclips:
        #     if movieclip.export_name != None:
        #         writer.writeInt16(movieclip.clip_id)

        # for movieclip in self.movieclips:
        #     if movieclip.export_name != None:
        #         writer.writeUInt8(len(movieclip.export_name))
        #         writer.writeChar(movieclip.export_name)

        all_objects = self.textures + self.shapes + self.movieclips + self.textfields + self.matrix2x3 + self.colortransforms + self.unknowns

        for object in all_objects:
            writer.writeUByte(object.data_type)

            data = object.export()

            writer.writeInt32(len(data))
            writer.write(data)
        
        writer.writeUByte(0) #1 Byte "type"
        writer.writeInt32(0) #4 Bytes "length"

        return writer.buffer

