# Experiments for fast live update
# Adapted from the opencv face detect examples
# 
# Volker Hilsenstein at Monash Edu

import numpy as np
from qtpy.QtCore import QThread
import napari
import time
import cv2


class ThreadVideo(QThread):
    def __init__(self, layer_, shape_layer_, capture_, casc_):
        QThread.__init__(self)
        self.layer_ = layer_
        self.capture_ = capture_
        self.casc_ = casc_
        self.shapes_ = shape_layer_
    
    def run(self):
        while True:
            ret, frame = self.capture_.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            #Detect faces in the image
            faces = self.casc_.detectMultiScale(
                 gray,
                 scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
            rects=[]
            for (x, y, w, h) in faces:
                rects.append(np.array([[y,x], [y,x+w], [y+h, x+w], [y+h,x]]))
            self.shapes_.data = rects
            self.layer_.data = rgb
        


def loop():
    with napari.gui_qt():
        # load the haar classifier
        casc = cv2.CascadeClassifier("C:/Users/Volker/Dropbox/Github/NapariPlayground/LiveUpdate/cascade.xml")
        # create the captur device and grab an initial image
        capture = cv2.VideoCapture(0)
        ret, frame = capture.read()
        # initiate viewer, image layer and shape layer
        viewer = napari.Viewer()
        layer = viewer.add_image(frame)
        shape_layer = viewer.add_shapes([])

        t = ThreadVideo(layer, shape_layer, capture, casc)
        t.start()
            

loop()