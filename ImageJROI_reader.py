# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:37:22 2017

@author: Andrew
"""

import os

import pandas as pd
import h5py
import tifffile as tf
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


#%%


dd = r'170201\G3_Im004_MC'
fd_file = 'F_data_from_cropped.hdf5'

with h5py.File(os.path.join(dd,fd_file), 'r') as f:
    f_data = {k:np.array(v) for k,v in f.items()}

#%%

with PdfPages('figures/G3_Im004_MC_rawF.pdf') as pdf:
    for roi, data in f_data.items():
        
        fig, ax = plt.subplots(ncols = 2, nrows = 2, figsize = (10,10))
        fig.suptitle(roi)        
        
        ax[0,1].imshow(data,
                    aspect = 'auto',
                    extent = [0, data.shape[1]/30, 
                              0, data.shape[0]],
                 )
        
        mask = tf.imread(os.path.join(dd,'Masks', roi+'.tiff'),)
        ax[0,0].imshow(mask,)
        
        pdf.savefig()        
        plt.close('all')
#%%



'''
0-3     "Iout"
4-5     version (>=217)
6-7     roi type
8-9     top
10-11   left
12-13   bottom
14-15   right
16-17   NCoordinates
18-33   x1,y1,x2,y2 (straight line)
34-35   stroke width (v1.43i or later)
36-39   ShapeRoi size (type must be 1 if this value>0)
40-43   stroke color (v1.43i or later)
44-47   fill color (v1.43i or later)
48-49   subtype (v1.43k or later)
50-51   options (v1.43k or later)
52-52   arrow style or aspect ratio (v1.43p or later)
53-53   arrow head size (v1.43p or later)
54-55   rounded rect arc size (v1.43p or later)
56-59   position
60-63   header2 offset
64-       x-coordinates (short), followed by y-coordinates



'''

with open(roi_file, 'rb') as f:
    header = f.read(64)
    points = np.fromfile(f, dtype='>i2')

def read_be(bytes):
    return int.from_bytes(bytes, 'big')

if header[:4] != b'Iout':
    print ("Not an ImageJ ROI")


version = read_be(header[4:6])
roi_type = read_be(header[6:8])
top = read_be(header[8:10])
left = read_be(header[10:12])
bottom = read_be(header[12:14])
right = read_be(header[14:16])
NCoordinates = read_be(header[16:18])
x1,y1,x2,y2 = (read_be(header[18:22]),
               read_be(header[22:26]),
               read_be(header[26:30]),
               read_be(header[30:34]),
               )
stroke_width = read_be(header[34:36])
ShapeRoi_size = read_be(header[36:40])
stroke_color = read_be(header[40:44])
fill_color = read_be(header[44:48])
subtype = read_be(header[48:50])
options = read_be(header[50:52])
arrow_style = read_be(header[52:53])
arrow_head_size = read_be(header[53:54])
rounded_rect_arc_size = read_be(header[54:56])
position = read_be(header[56:60])
header2_offset = read_be(header[60:65])
#%%

import numpy as np
import matplotlib
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
