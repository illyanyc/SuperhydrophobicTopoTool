from PIL import Image
import os

def convert(path):
    im = Image.open(path)
    ext = path
    newname = ext+".png"
    im.save(newname)
    print newname