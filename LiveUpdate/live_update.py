# Experiments for fast live update
# inspired by and based on code 
# https://github.com/napari/napari/issues/465

# this is based on the original code snipped with update interval reduced to 0.1
# note that the approach mentioned in the comments below that, i.e.
# layer._node.set_data(img)
# layer._node.update()
# did not work (no attribute _node). There may have been some internal changes to napari since.

import numpy as np
import napari
from qtpy.QtCore import QThread
import time
from datetime import datetime


def send_random(layer_):
    # number of images to stream
    num_images = 1000
    
    # time between image assignment
    update_interval = 0.05

    # pause so we can observe beginning/end of visual update
    time.sleep(2)

    print('from another thread')
    start = datetime.now()
    for k in range(num_images):

        time.sleep(update_interval)

        dat = np.random.random((512, 512))
        layer_.data = dat
        
        # check that data layer is properly assigned and not blocked?
        while layer.data.all() != dat.all():
            layer_.data = dat

    stop = datetime.now()
    print("time per update = "+
          str((stop-start).microseconds/num_images))


class ThreadRandom(QThread):

    def __init__(self, layer_):
        QThread.__init__(self)
        self.layer_ = layer_

    def run(self):
        send_random(self.layer_)


with napari.gui_qt():
    # create the viewer with an image

    data = np.random.random((512,512))
    viewer = napari.Viewer()
    layer = viewer.add_image(data)

    t = ThreadRandom(layer)
    t.start()