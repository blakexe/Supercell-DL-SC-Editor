from sc import SC
import os
from PIL import Image
from argparse import ArgumentParser
from sc_compression.compressor import Compressor
from sc_compression.decompressor import Decompressor

dir_path = os.path.dirname(os.path.realpath(__file__))

parser = ArgumentParser(description='Export and import textures from _dl.sc files. (That is not decompressed yet)')

parser.add_argument('path_to_sc')
parser.add_argument('--export', help='Export .png', action='store_true')
parser.add_argument('--importpng', help='Import specified .png')

args = parser.parse_args()

def start():

    sc = SC()
    decompressor = Decompressor()
    compressor = Compressor()

    with open(args.path_to_sc, "rb") as f:
        data = decompressor.decompress(f.read())
        
    if args.export:
        sc.import_sc(data)
        texture = sc.textures[0]
        texture.image.save(os.path.join(dir_path, "exported.png"))
        print("Done!")
    else:
        try:
            new_png = args.importpng
        except AttributeError:
            print("You must specify whether to --export or --import {png} in the arguments")
        else:
            sc.import_sc(data)

            new_image = Image.open(new_png)

            sc.textures[0].image = new_image

            new_data = sc.export_sc()

            with open(args.path_to_decompiled_sc, "wb") as f:
                f.write(compressor.compress(new_data, 2))
            print("Done!")

if __name__ == "__main__":
    start()