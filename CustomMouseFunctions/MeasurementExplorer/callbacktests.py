import napari


def print_attributes(my_object):
    attributes = [attr for attr in dir(my_object) 
              if not attr.startswith('__')]
    for attr in attributes:
        print(attr, getattr(my_object, attr))


def show_event_attrs(event):
    print(event)
    print_attributes(event)
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