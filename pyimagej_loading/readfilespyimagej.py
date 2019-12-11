#
# This is a code snippet shared by Curtis Rueden on the image.sc forum
# https://forum.image.sc/t/read-images-with-imagej-display-them-with-napari/32156
# 

"""
Read images with ImageJ; display them with Napari.
"""

import napari, sys

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

    for i in range(1, len(sys.argv)):
        path = sys.argv[i]
        print('--> Reading {}'.format(path))

        dataset = ij.io().open(path)
        image = ij.py.from_java(dataset)

        if i == 1:
            viewer = napari.view_image(image)
        else:
            viewer.add_image(image)

    ij.getContext().dispose()

    viewer.grid_view()