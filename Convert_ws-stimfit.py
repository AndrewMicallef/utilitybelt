#!/usr/bin/env python

from __future__ import division
import os
import datetime

import h5py #stfio will crap out if it is loaded before h5py
import stfio
import numpy as np
import argparse
from utilitybelt import ws


# a work in progress. so far the output is in V so you must know the conversions
# on the aquisition channels


def convert_ws_to_stfio(infile):

    wsfile = ws.wsfile(infile)

    data = wsfile.data()
    units = wsfile.unitslist
    chlist = []

    for channel, traces in data.iteritems():

        seclist = [stfio.Section(trace) for trace in traces
                                            if np.any(trace)]
        chlist.append(stfio.Channel(seclist))
        chlist[-1].yunits = units[channel]
        chlist[-1].name = channel
    
    rec = stfio.Recording(chlist)
    rec.date = wsfile.dstamp.strftime("%Y-%m-%d")
    rec.time = wsfile.dstamp.strftime("%H-%M-%S")
    rec.dt = 1000.0/wsfile.SampleRate
    rec.dt
    rec.xunits = 'ms'
   
    return rec

parser = argparse.ArgumentParser(description="convert wavesurfer.h5 to stimfit.h5")
parser.add_argument("file", help = "file to convert")
parser.add_argument("-o", "--outfile", default = "", help = "name of output file. infile.h5 by default")

args = parser.parse_args()

if __name__ == '__main__':
    infile = args.file
    outfile = args.outfile
    
    if os.name == 'nt':
        outfile = outfile.replace("\\", "/")
    
    rec = convert_ws_to_stfio(infile)

    if not outfile:
        outfile = os.path.split(infile)[1]
        outfile = outfile.split(".")[0] #remove fie ext
        outfile = "stimfit_%s.h5" %outfile
    
    rec.write(outfile)
    
    quit()