import numpy as np

from PIL import Image
from tivars import *
from tivars.PIL import *


# Load an image using a PIL decoder
img = Image.open("../tests/data/var/Image1.8ca")
img.show()


# Alternatively, load the image manually
ti_img = TIImage()
ti_img.open("../tests/data/var/Image1.8ca")

arr = np.asarray(ti_img.array(), dtype=np.uint8)
img = Image.fromarray(arr, mode=ti_img.pil_mode)
img.show()

# Each pixel becomes a 2x2 square of pixels on-calc
img.resize((266, 166), resample=Image.NEAREST).show()
