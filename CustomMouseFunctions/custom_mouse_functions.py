"""
Display one 4-D image layer using the add_image API
"""

from skimage import data
from skimage.morphology import binary_dilation, binary_erosion
from scipy import ndimage as ndi
import numpy as np
import napari
from qtpy import QtWidgets, QtGui, QtCore
from skimage.measure import regionprops_table
import pandas as pd
from pandas_qt_table import pandasModel
from qtpy.QtWidgets import QApplication, QTableView


def create_regionprop_text(df, index):
    if index is None: # In viewer, but not over a pixel
        oblabel = "outside"
    if index == 0:
        oblabel = "background"
    else:
        oblabel = str(index)
    subset = df[df["label"]==index]
    text = f"<h1> Object ID: {oblabel}<h1><p>"
    for col in df.columns:
        text += f"{col}: {str(subset[col].values)}<br>"
    return(text)

with napari.gui_qt():
    np.random.seed(1)
    viewer = napari.Viewer()
    blobs = data.binary_blobs(length=128, volume_fraction=0.1, n_dim=2)
    labeled = ndi.label(blobs)[0]

    # Measure some properties of the blobs and create a DataFrame
    measurements = regionprops_table(label_image= labeled, properties=('label','area', 'eccentricity', 'solidity'))
    df = pd.DataFrame(measurements)
    # Create a Qt TableView from the pandas table
    model = pandasModel(df[df.label==1]) # dirty hack so we just have a one-row table
    view = QTableView()
    view.setModel(model)
    view.resize(800, 200)
    view.show()
    text = QtWidgets.QLabel("")
    text.show()
    labels_layer = viewer.add_labels(labeled, name='blob ID')

    @viewer.mouse_drag_callbacks.append
    def get_ndisplay(viewer, event):
        if 'Alt' in event.modifiers:
            print('viewer display ', viewer.dims.ndisplay)

    @labels_layer.mouse_move_callbacks.append
    def move(layer, event):
        #print(event.pos)
        label_nr = layer.get_value()
        subset = df[df["label"]== label_nr]
        model.updateData(subset)
        text.setText(create_regionprop_text(df, label_nr))


    @labels_layer.mouse_drag_callbacks.append
    def get_connected_component_shape(layer, event):
        cords = np.round(layer.coordinates).astype(int)
        val = layer.get_value()
        if val is None:
            return
        if val != 0:
            data = layer.data
            binary = data == val
            if 'Shift' in event.modifiers:
                binary_new = binary_erosion(binary)
                data[binary] = 0
                data[binary_new] = val
            else:
                binary_new = binary_dilation(binary)
                data[binary_new] = val
            size = np.sum(binary_new)
            layer.data = data
            msg = f'clicked at {cords} on blob {val} which is now {size} pixels'
        else:
            msg = f'clicked at {cords} on background which is ignored'
        layer.status = msg
        print(msg)
