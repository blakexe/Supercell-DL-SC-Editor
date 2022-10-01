from cgitb import text
from dataclasses import replace
from sc_objects.sc_object import ScObject
from utils.reader import Reader
from utils.writer import Writer
from PIL import Image, ImageDraw, ImageOps

class ShapeChunk(ScObject):
    def __init__(self, main_sc, data):
        ScObject.__init__(self, main_sc, data, 0)
        self.chunk_type = None
        self.xy_points = []
        self.uv_points = []
        self.chunk_id = None
        self.shape_id = None

    def round_school(self, x):
        i, f = divmod(x, 1)
        return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))


    def parse_data(self):
        reader = Reader(self.data, 'little')

        self.texture_id = reader.readByte()
        shape_point_count = reader.readByte()
        texture = self.main_sc.textures[self.texture_id]

        print("\n\n")
        for i in range(shape_point_count):
            x = reader.readInt32() * 0.1
            y = reader.readInt32() * 0.1

            # reader.i -= 8
            # print(f"x bytes: {reader.read(4)}, y bytes: {reader.read(4)}")

            self.xy_points.append((x, y))
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
        print(f"\n\n")
                
    def render(self) -> Image:
        texture_image = self.main_sc.textures[self.texture_id].image

        mask_im = Image.new("L", texture_image.size) #8 bit black and white image

        mask_drawer = ImageDraw.Draw(mask_im) #PIL Drawing methods
        mask_drawer.polygon(self.uv_points, fill="#FFFFFF", outline=None)

        rendered = Image.composite(texture_image, Image.new("RGBA", texture_image.size), mask_im)

        rendered = rendered.crop(mask_im.getbbox())

        return rendered
    
    def replace(self, replacement_image: Image):
        texture = self.main_sc.textures[self.texture_id]
        texture_image = texture.image

        mask_im_sheet = Image.new("L", texture_image.size) #8 bit black and white image

        #Render mask on sheet and isolated
        mask_drawer = ImageDraw.Draw(mask_im_sheet) #PIL Drawing methods
        mask_drawer.polygon(self.uv_points, fill="#FFFFFF", outline=None)
        mask_im_isolated = mask_im_sheet.crop(mask_im_sheet.getbbox())

        print(f"Mask im sheet size: {mask_im_sheet.size}, mask im isolated size: {mask_im_isolated}")

        #Resize replacement if not matching
        if replacement_image.size != mask_im_isolated.size:
            replacement_image = replacement_image.resize(mask_im_isolated.size)

        print(f"Replacement new size: f{replacement_image.size}")

        #Mask over the replacement
        replacement_image = Image.composite(replacement_image, Image.new("RGBA", replacement_image.size), mask_im_isolated)

        #Remove original from sheet
        texture_image = Image.composite(texture_image, Image.new("RGBA", texture_image.size), ImageOps.invert(mask_im_sheet))

        #Put modified in its place
        bounds = mask_im_sheet.getbbox()
        texture_image.paste(replacement_image, [bounds[0], bounds[1]])

        texture.image = texture_image

    def export(self) -> bytes:
        writer = Writer("little")

        texture = self.main_sc.textures[self.texture_id]

        writer.writeUByte(self.texture_id) #texture id
        writer.writeByte(len(self.uv_points)) #shape point count

        for point in self.xy_points:
            writer.writeInt32(int(point[0] / 0.1)) # x
            writer.writeInt32(int(point[1] / 0.1)) # y
        if self.chunk_type == 22:
            for point in self.uv_points:
                writer.writeUInt16(self.round_school((point[0] / texture.image.width) * 65535)) # u
                writer.writeUInt16(self.round_school((point[1] / texture.image.height) * 65535)) # v
        else:
            for point in self.uv_points:
                writer.writeUInt16(point[0]) # u
                writer.writeUInt16(point[1]) # v
        
        return writer.buffer
