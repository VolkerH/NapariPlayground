# This code snippet is (mostly) from a blog post by Talley Lambert
# https://napari.org/tutorials/dask

import napari
import pycudadecon
from functools import partial
from skimage import io
from dask_image.imread import imread


# prepare some functions that accept a numpy array
# and return a processed array

def last3dims(f):
    # this is just a wrapper because the pycudadecon function
    # expects ndims==3 but our blocks will have ndim==4
    def func(array):
        return f(array[0])[None, ...]
    return func


def crop(array):
    # simple cropping function
    return array[:, 2:, 10:-20, :500]


if  if __name__ == "__main__":
    import sys
    import os.sep as sep
    stackfolder = sys.argv[1]
    psffile = sys.argv[2]
    print(f"Stackfolder: {stackfolder}")
    print(f"PSF file: {psffile}")
    # load stacks with da :sk_image, and psf with skimage
    stack = imread(stackfolder+sep+"*.tif")
    psf = io.imread("psffile")

    # https://docs.python.org/3.8/library/functools.html#functools.partial
    deskew = last3dims(partial(pycudadecon.deskew_gpu, angle=31.5))
    deconv = last3dims(partial(pycudadecon.decon, psf=psf, background=10))
    # note: this is done in two steps just as an example...
    # in reality pycudadecon.decon also has a deskew argument

    # map and chain those functions across all dask blocks
    deskewed = stack.map_blocks(deskew, dtype="uint16")
    deconvolved = deskewed.map_blocks(deconv, dtype="float32")
    cropped = deconvolved.map_blocks(crop, dtype="float32")

    # put the resulting dask array into napari.
    # (don't forget the contrast limits and is_pyramid==False !)
    with napari.gui_qt():
        v = napari.view_image(
            cropped,
            contrast_limits=[90, 1500],
            is_pyramid=False,
            ndisplay=3,
            scale=(3, 1, 1),
        )


