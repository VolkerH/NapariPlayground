import napari
from skimage.io import imread
import numpy as np 


vol = imread(".\Data\droso_ovarioles.tif")

# some bugs in napari discovered

# Variant 1
# with subsampling ... this crashes in OpenGL\wrapper.py
vol = vol[::2,::2,::2].astype(np.float64)
print(vol.flags)
# Variant 2
# no subsampling, but changing dtype to float64
# vol = vol.astype(np.float64)


# Variant 3
# original dtype
# do nothing
print(vol.dtype) # it is float32 for the dtype


with napari.gui_qt(): 
    viewer = napari.Viewer()
    viewer.add_image(vol)