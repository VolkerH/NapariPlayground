import requests
import pathlib
import h5py 
import napari 
import numpy as np

# Simple napari layer viewer for my Multilabelling data
# Volker Hilsenstein
#
# See 
# https://github.com/VolkerH/Multilabelling_HDF5_View



#
# Download example dataset from Dropbox
# 
def extract_filename_from_url(url):
    try:
        end = url[url.rfind('/')+1:]
        filename = end[:end.find('?')]
        return filename
    except: 
        return None
    
def download_from_dropbox(url, outfile=None):
    url = url.replace('?dl=0', '')
    url = url.replace('?dl=1', '')
    if not '?raw=1' in url:
        url += "?raw=1"
    r = requests.get(url, allow_redirects=True)
    if not outfile:
        outfile = extract_filename_from_url(url)
    if outfile:
        open(outfile, 'wb').write(r.content)

url = "https://www.dropbox.com/s/ygv4tsg0n936l7e/field--X02--ctrl1.hdf5?dl=0"
filename = extract_filename_from_url(url)
if not pathlib.Path(filename).exists():
    print("Downloading dataset. This may take a while.")
    download_from_dropbox(url)


# Visualize
# Open sample data set and create one image layer per antibody
# 
with h5py.File(filename,"r") as f:
    # get image dimensions
    n_AB = f["ordering"].shape[0]
    antibody_keys = list(map(lambda x: "AB_"+f["ordering"][x].decode('utf-8'), range(n_AB)))
    if len(antibody_keys) == 0:
        print("No Antibodies found")
        exit()
    with napari.gui_qt(): 
        viewer = napari.Viewer()
        
        # add Antibody layers
        for key in antibody_keys:
            viewer.add_image(f[key]['imaging']['data']['stack'][:,:,1,:], name=key[3:])
            print(f[key]['imaging']['registration']['displacement'][:])
        
        # add DAPI from first acquistion
        viewer.add_image(f[antibody_keys[0]]['imaging']['data']['stack'][:,:,0,:], name="DAPI",)
        
        # adjust blending modes, visibility and apply registration as layer translations
        for layer in viewer.layers:
            key = "AB_" + layer.name
            layer.blending="additive"
            if layer.name == "DAPI":
                layer.visible = True
                layer.colormap = 'blue'
            else:
                layer.visible = False
                layer.colormap = 'green'
                xtrans, ytrans =   f[key]['imaging']['registration']['displacement'][:]
                layer.translate = [xtrans, ytrans, 0]
                print(f"Applied registration transformation to layer {layer.name}. x,y,z - displacement {layer.translate}.")