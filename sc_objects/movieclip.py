# from sc_objects.sc_object import ScObject
# from utils.reader import Reader

# class MovieClip(ScObject):
#     def __init__(self, main_sc, data: bytes, data_type: int):
#         ScObject.__init__(self, main_sc, data, data_type)

#         self.id = -1
#         self.export_name = None
#         self.fps = None
#         self.frames_count = None
#         self.transforms = {}
#         self.shapes = []
#         self.blends = []

#         self.points = []

#     def parse_data(self):
#         reader = Reader(self.data, 'little')

#         print(f"data type: {self.data_type}")
#         print(self.data)

#         self.id = reader.readUInt16()

#         self.export_name = self.main_sc.movie_clip_info[self.id]
#         self.fps = reader.readByte()
#         self.frames_count = reader.readUInt16()

#         if self.data_type in (3, 14,):
#             pass
#         else:
#             transforms_count = reader.readUInt16()

#             for i in range(transforms_count):
#                 bind_id = reader.readUInt16()
#                 matrix_id = reader.readUInt16()
#                 color_transform_id = reader.readUInt16()

#                 if not (bind_id in self.transforms):
#                     self.transforms[bind_id] = {'matrices': [], 'color_transforms': []}
#                 self.transforms[bind_id]['matrices'].append(matrix_id)
#                 self.transforms[bind_id]['color_transforms'].append(color_transform_id)

#         reader.readUInt16() #2 unused bytes: 65535

#         binds_count = reader.readUInt16()

#         print(f"binds count: {binds_count}")

#         for i in range(binds_count):
#             shape_id = reader.readUInt16()  # shape id

#             #Get shape from main SC
#             shapes = [shape for shape in self.main_sc.shapes if shape.shape_id == shape_id]

#             self.shapes += shapes

#         if self.data_type in (12, 35,):
#             for i in range(binds_count):
#                 blend = reader.readUInt16()  # blend
#                 self.blends.append(blend)

#         for i in range(binds_count):
#             reader.readUInt16()  # bind_name

#         while True:
#             frame_tag = reader.readUByte()
#             frame_length = reader.readInt32()

#             if frame_tag == 0:
#                 break

#             if frame_tag == 11:
#                 reader.readInt16()  # frame_id
#                 reader.readString()  # frame_name
#             else:
#                 reader.read(frame_length)

#     def render(self):
#         pass

from sc_objects.sc_object import ScObject
from utils.reader import Reader

class MovieClip(ScObject):
    def __init__(self, main_sc, data: bytes, data_type: int):
        ScObject.__init__(self, main_sc, data, data_type)
        self.shapes = []
        self.export_name = None

    def parse_data(self):
        '''
        This function was directly translated from Ultrapowa's SC Editor and I have literally no idea what it actually does
        
        If you are able to decipher and comment what all of this does please help :)
        '''

        reader = Reader(self.data, "little")

        self.clip_id = reader.readInt16()
        reader.readByte()
        self.frame_count = reader.readInt16()

        try:
            self.export_name = self.main_sc.movie_clip_info[self.clip_id]
        except:
            try:
                self.export_name = self.main_sc.movie_clip_info[self.clip_id + 1]
            except:
                pass

        if self.data_type != 14:
            count1 = reader.readInt32()
            shape_list_1 = []
            for i in range(count1):
                for i in range(3):
                    shape_list_1.append(reader.readInt16())
            
        count2 = reader.readInt16()
        print(f"count 2: {count2}")
        shape_list_2 = []
        for i in range(count2):
            shape_id = reader.readInt16()
            shape_list_2.append(shape_id)
            for shape in self.main_sc.shapes:
                if shape.shape_id == shape_id:
                    self.shapes.append(shape)
                    break
        if self.data_type == 12:
            reader.read(count2)
        
        #Read ascii
        for i in range(count2):
            string_length = reader.readByte()
            if string_length < 255:
                #??? how would a byte be over 255 bits like what
                reader.read(string_length)
                
        v26 = None #<-- I have no idea what this variable even means
        while True:
            while True:
                while True:
                    v26 = reader.readByte()
                    reader.readInt32() #<--- okay why? huh? 4 unused bytes?
                    if v26 != 5: #Okay but why?
                        break
                if v26 == 11: #Again, why this number? Thanks Ultrapowa for not specifying this in your code
                    frame_id = reader.readInt16()
                    frame_name_length = reader.readByte()
                    if frame_name_length < 255:
                        reader.read(frame_name_length)
                else:
                    break
            if v26 == 0:
                break
            print(f"Unknown tag: {v26}")

    def get_id(self):
        return self.clip_id

    def set_name(self, name: str):
        self.name = name