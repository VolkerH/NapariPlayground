import napari
from skimage.measure import regionprops_table
import pandas as pd
#from qtpy.QtWidgets import QApplication, QTableView
from qtpy import QtWidgets 

def print_attributes(my_object):
    attributes = [attr for attr in dir(my_object) 
              if not attr.startswith('__')]
    for attr in attributes:
        print(attr, getattr(my_object, attr))

def create_regionprop_text(df, index):
    if index is None: # In viewer, but not over a pixel
        oblabel = "outside"
    if index == 0:
        oblabel = "background"
    else:
        oblabel = str(index)
    subset = df[df["label"]==index]
    text = f"<h3> Object ID: {oblabel}</h3><p>"
    for col in df.columns:
        text += f"{col}: {str(subset[col].values[:])}<br>"
    return(text)

def collect_compatible_layers(layers):
    """
        Given a  napari viewer layers list, find all layers of type Labels
        and for each of those find all image layers of compatible shape.

        This could be used to update a GUI in which the objects to be
        measured using regionprops can be selected from a drop-down menu
        and compatible image layers (for intensity statistics) can be
        selected using tick boxes
    """
    matched_layers = []
    label_layers = []
    for layer in layers:
        if isinstance(layer, napari.layers.labels.labels.Labels):
            label_layers.append(layer)
    for label_layer in label_layers:
        label_shape = label_layer.data.shape
        image_layers = []
        print(label_shape)
        for layer in layers:
            if not isinstance(layer, napari.layers.labels.labels.Labels) and isinstance(layer, napari.layers.image.image.Image):
                print("---> ", layer.data.shape)
                if layer.data.shape == label_shape:
                    image_layers.append(layer)
                elif (layer.data.shape[-1] == 3 or layer.data.shape[-1] == 4) and layer.data.shape[:-1] == label_shape: 
                    print("labels layer x,y dimensions match RGB / RGBA image")
                    image_layers.append(layer)
        if len(image_layers):
            matched_layers.append({"label_layer": label_layer, "compatible_image_layers": image_layers})
    return matched_layers


def measure(viewer):
    """
    
    """
    to_measure = check_selected_layers_compatible(viewer.layers)
    print("to_measure", to_measure)
    if not bool(to_measure):
        print("Selected layers not compatible with measurments")
        return

    label_layer = to_measure['label_layer']
    im_layers =  to_measure['compatible_image_layers']
    #
    print(f"Measuring objects in layer {label_layer}")
    for imlayer in im_layers:
        print(f"intensity image {imlayer}")

    # properties
    # these would have to be gotten from a GUI with checkboxes
    
    # turns out not all properties are compatible with 3D labels, e.g. orientation
    props_all = ('label',)
    props_shape = ('area', 'major_axis_length', 'minor_axis_length', 'orientation',)
    props_intensity = ('mean_intensity', 'max_intensity', 'min_intensity', )
    tables = []
    if len(im_layers) == 0:
        # just measure properties_shape as we don't have an intensity image
        table = regionprops_table(label_layer.data, properties=props_all + props_shape)
    else:
        table = regionprops_table(label_layer.data, im_layers[0].data, 
                properties=props_all+props_shape+props_intensity)
    tables.append(table)
    # measure any additional intensity layers
    for im_layer in im_layers[1:]:
        table = regionprops_table(label_layer.data, im_layers[0].data, 
        properties=porps_all+props_shape+props_intensity)
        tables.append[table]
    
    dfs = list(map(pd.DataFrame, tables))
    print(dfs)
    
    text = QtWidgets.QLabel(create_regionprop_text(dfs[0], 0))
    text.show()
    
    @label_layer.mouse_move_callbacks.append
    def move(layer, event):
        #print(event.pos)
        label_nr = layer.get_value()
        df=dfs[0]
        subset = df[df["label"]== label_nr]
        text.setText(create_regionprop_text(df, label_nr))
    # TODO activate hover_callback showing measurments

def check_selected_layers_compatible(layers):
    """
    Given the layers list, goes through all selected layers and checks
    whether they are compatible with runnning skimage regionprops, i.e.

    * there must be exactly one labels layer selected
    * additionaly selected image layers must have a shape that is compatible with
      the labels layer

    
    Parameters
    ----------
    layers : napari.viewer.layers
    
    returns: dictionary with keys "label_layer" and "comaptible image layers"
    """
    
    label_layers = []
    # todo: change to filter statement which is nicer
    
    for layer in layers:
        if layer.selected and isinstance(layer, napari.layers.labels.labels.Labels):
            label_layers.append(layer)
    if not len(label_layers):
        print("no label layer in selection, nothing to measure.")
        return {}
    if len(label_layers) > 1:
        print("more than one label layer in selection, not sure what to measure.")
        return {}

    # search for image layers of compatible shape
    label_layer=label_layers[0]
    label_shape = label_layer.data.shape
    image_layers = []
    print(label_shape)
    for layer in layers:
        if layer.selected:
            if not isinstance(layer, napari.layers.labels.labels.Labels) and isinstance(layer, napari.layers.image.image.Image):
                print("---> ", layer.data.shape)
                if layer.data.shape == label_shape:
                    image_layers.append(layer)
                #elif (layer.data.shape[-1] == 3 or layer.data.shape[-1] == 4) and layer.data.shape[:-1] == label_shape: 
                #    print("labels layer x,y dimensions match RGB / RGBA image")
                #    image_layers.append(layer)
                else:
                    print(f"layer {layer} has incompatible shape.")
                    return {}
            elif not (layer is label_layer):
                    print(f"layer {layer} has incompatible type")
    return {"label_layer": label_layer, "compatible_image_layers": image_layers}

def show_event_attrs(event):
    return # disable temporarily
    print(event)
    for layer in viewer.layers:
        print(f'Layer {layer}:')
        #print_attributes(layer)
        #print(type(layer))
        if isinstance(layer, napari.layers.shapes.shapes.Shapes):
            print("Shape layer")
        elif isinstance(layer, napari.layers.labels.labels.Labels):
            print("Labels layer")
        elif isinstance(layer, napari.layers.image.image.Image):
            print("Image layer")
        else:
            print("other layer")
        if  layer.selected:
            print("selected")
        else:
            print("not selected")


with napari.gui_qt():
    viewer = napari.Viewer()
    viewer.layers.events.emitters['added'].connect(show_event_attrs)
    viewer.layers.events.emitters['removed'].connect(show_event_attrs)
    viewer.layers.events.emitters['reordered'].connect(show_event_attrs)

    viewer.bind_key('9', measure)



    # currently there does not seem to be an event when a layer has been renamed
    # check at QT level: QtLayerWidget.changeText _on_layer_name_change

# emitters in viewer.layers.events
# 'added', 'removed', 'reordered'


#<class 'napari.util.event.Event'>
#['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_blocked', '_handled', '_native', '_pop_source', '_push_source', '_sources', '_type', 'blocked', 'handled', 'index', 'item', 'native', 'source', 'sources', 'type']

# emitters in viewer.layer['Shapes'].events.emitters
# stmp.events.emitters
# Out[15]: 
# OrderedDict([('refresh', <napari.util.event.EventEmitter at 0x1ea5fef6908>),
#              ('set_data', <napari.util.event.EventEmitter at 0x1ea5fef65f8>),
#              ('blending', <napari.util.event.EventEmitter at 0x1ea5fef6f28>),
#              ('opacity', <napari.util.event.EventEmitter at 0x1ea5fef6128>),
#              ('visible', <napari.util.event.EventEmitter at 0x1ea5fef6ac8>),
#              ('select', <napari.util.event.EventEmitter at 0x1ea5fef6a90>),
#              ('deselect', <napari.util.event.EventEmitter at 0x1ea5fef6c88>),
#              ('scale', <napari.util.event.EventEmitter at 0x1ea5fef6710>),
#              ('translate', <napari.util.event.EventEmitter at 0x1ea5fef6a20>),
#              ('data', <napari.util.event.EventEmitter at 0x1ea5fef6860>),
#              ('name', <napari.util.event.EventEmitter at 0x1ea5fef6ef0>),
#              ('thumbnail', <napari.util.event.EventEmitter at 0x1ea5fc759e8>),
#              ('status', <napari.util.event.EventEmitter at 0x1ea5fc757f0>),
#              ('help', <napari.util.event.EventEmitter at 0x1ea5fc75e80>),
#              ('interactive',
#               <napari.util.event.EventEmitter at 0x1ea5fc75da0>),
#              ('cursor', <napari.util.event.EventEmitter at 0x1ea5fc750b8>),
#              ('cursor_size',
#               <napari.util.event.EventEmitter at 0x1ea5fc75fd0>),
#              ('editable', <napari.util.event.EventEmitter at 0x1ea5fc75208>),
#              ('mode', <napari.util.event.EventEmitter at 0x1ea5fc75128>),
#              ('edge_width', <napari.util.event.EventEmitter at 0x1ea521490b8>),
#              ('edge_color', <napari.util.event.EventEmitter at 0x1ea52149668>),
#              ('face_color', <napari.util.event.EventEmitter at 0x1ea52149d30>),
#              ('highlight', <napari.util.event.EventEmitter at 0x1ea52149dd8>)])