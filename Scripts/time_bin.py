# 3:33 PM 12/8/2015
from __future__ import division
import sys
from timeit import default_timer as timer

from utilitybelt.ThorImage import thorfile as TF
import time
import xml.etree.ElementTree as ET

import os
import numpy as np
from tifffile import imsave

usage = """
time_bin.py FILE

on windows:
    > for /f %f in ('dir /s /b Ima*.RAW') do time_bin.py %f
"""

if len(sys.argv) < 2:
    print usage
    quit()

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

filename=sys.argv[1]
chan = ["G", "R", "", ""]
method = 'sum'
    
filename =  filename.replace("\\", "/")

inpath = os.path.split(filename)[0]
tiffpath = "%s/tiff" %inpath
summarypath = "%s/summary" %inpath

basename = os.path.split(inpath)[1]

#the method to use to create summary
methods = { 
    'sum' : np.sum,
    'min' : np.min,
    'max' : np.max,
    'avg' : np.mean,
    'std' : np.std,
    'none': None,
}

if not(os.path.exists(tiffpath)):
    os.makedirs(tiffpath)
    print "\tcreated:", tiffpath

if not(os.path.exists(summarypath)):
    os.makedirs(summarypath)
    print "\tcreated:", summarypath

xmlfile = "Experiment.xml"        
XMLtree = ET.parse("%s/%s" %(inpath, xmlfile))
root = XMLtree.getroot()

name = root.find("Name").attrib['name']

framerate = root.find("LSM").attrib['frameRate']
framerate = framerate.split(" fps")[0]
framerate = int(num(framerate))
    
if any(['1sbin' in f 
        for f in os.listdir(summarypath)]):
    print "\ttiffs already found"
    quit()

start = timer()    
print "stacking...",
img = TF(inpath).stack(0)
print "\r...stacked (%5.3g s)" %(timer() - start)

start = timer()
print "binning...",
img_bin = np.array([img[i:i+framerate].mean(axis=0) 
          for i in xrange(0,img.shape[0], framerate)])
print "\r...binned (%5.3g s)" %(timer() - start)

start = timer()
print "saving...",
imsave(
        '%s/%s_1sbin_G.tiff' %(summarypath, name),
        img_bin.astype('int16'),
        )
print "\r...saved (%.2g s)" %(timer() - start)
