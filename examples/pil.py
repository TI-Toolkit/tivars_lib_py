import numpy as np

from PIL import Image
from tivars import *


# Load an image into PIL
ti_img = TIImage()
ti_img.open("../tests/data/var/Image1.8ca")

arr = np.asarray(ti_img.rgb_array(), dtype=np.uint8)
img = Image.fromarray(arr, mode=ti_img.pil_mode)
img.show()

# Each pixel becomes a 2x2 square of pixels on-calc
img.resize((266, 166), resample=Image.NEAREST).show()
