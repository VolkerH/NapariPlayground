#
# This is a based on two code snippets:
# 1. a snippet demonstrating reading files with pyimagej shared by Curtis Rueden on the image.sc forum
# https://forum.image.sc/t/read-images-with-imagej-display-them-with-napari/32156
# 2. a snippet demonstrating how to lazily read large stacks into napari using dask.delayed
# shared by Talley Lambert at https://napari.org/tutorials/dask
#
#


"""
Read images lazily using dask and ImageJ; display them with Napari.
"""

import napari, sys
from dask import delayed
import dask.array as da
from functools import partial

if len(sys.argv) <= 1:
    print('Please specify one or more images as arguments.')
    exit(1)

try:
    import imagej
except ImportError:
    raise ImportError("""This example uses ImageJ but pyimagej is not
    installed. To install try 'conda install pyimagej'.""")

with napari.gui_qt():

    print('--> Initializing imagej')
    ij = imagej.init('sc.fiji:fiji') # Fiji includes Bio-Formats.

    def ijreader(ijcontext, file):
        _dataset = ijcontext.io().open(file)
        return ijcontext.py.from_java(_dataset)

    # get a first dataset
    sample = ijreader(ij, sys.argv[1])
    print(f"dtype is {sample.dtype}")
    print(f"shape is {sample.shape}")
    
    lazy_imread = delayed(partial(ijreader, ij))  # lazy reader
    files = [sys.argv[i] for i in range(1, len(sys.argv)) ]
    lazy_arrays = [lazy_imread(fn) for fn in files]
    dask_arrays = [
        da.from_delayed(delayed_reader, shape=sample.shape, dtype=sample.dtype)
        for delayed_reader in lazy_arrays
    ]
    # Stack into one large dask.array
    stack = da.stack(dask_arrays, axis=0)
    print(stack.shape) 
    print(stack)
    viewer = napari.view_image(stack)

    