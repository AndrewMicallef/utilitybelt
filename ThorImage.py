from __future__ import division
import time
import xml.etree.ElementTree as ET
import sys
import argparse
from PIL import Image
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
#from tifffile import imsave

class thorfile:

    """
    This class holds the thorfile.
    to access the raw image use thorfile.img
    
    
    """
    
    def _num_(self, s):
        try:
            return int(s)
        except ValueError:
            return float(s)
    
    def _metadata_(self, element):
        "recursive walk through xml tree producing a dict"

        _dict = element.attrib

        children = element.getchildren()
        
        if children:
            for child in children:
                _dict[child.tag] = self._metadata_(child)

        return _dict

    
    
    def __init__(self, path, lite = False):
        
        self.path = path
        
        if not lite:
            self.read()
        
        xml_file = os.path.join(path, "Experiment.xml")
        xmltree = ET.parse(xml_file)
        xmlroot = xmltree.getroot()

        self.meta = self._metadata_(xmlroot)
        
        self.ww = self._num_(self.meta['LSM']['pixelX'])
        self.hh = self._num_(self.meta['LSM']['pixelY'])
        
    def stack(self, channel = 0):
        return self.raw.reshape(-1, self.hh, self.ww)[channel::4]

    def read(self):    
        raw_file = os.path.join(self.path, "Image_0001_0001.raw")
        self.raw = np.fromfile(raw_file, dtype='<u2')
    
    def clear(self):
        self.raw = None