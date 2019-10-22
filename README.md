# Napari Playground

Some of my experiments with [Napari](https://github.com/napari/napari). Still baby steps at this point.

## Multilabelling HDF5 viewer

A few years ago, I implemented a hdf5-based format and custom viewer for highly multiplexed 
fluorescence data, [see this Github repo](https://github.com/VolkerH/Multilabelling_HDF5_View).

I managed to implement most of the functionality (including registered display of layers) 
available in my custom viewer with a few lines of python using napari [Source Code](./Multilabelling/multilabel.py).

![](./Gallery/multilabelling.png)

## Simple label/object inspector demo

A quick and dirty hack, just to show what a label inspector could look like in napari. [Source Code](./CustomMouseFunctions/custom_mouse_functions.py)
![](./Gallery/napari_label_inspector.gif)
