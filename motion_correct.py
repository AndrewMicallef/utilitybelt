#!python3

import os
import numpy as np
import tifffile
import matplotlib.pyplot as plt
from timeit import default_timer as timer
import tqdm
from itertools import count

import sys

usage = """motion_correction.py filename

on windows do:
> for /f %f in ('dir /b /s *ChanG_mov.tiff') do motion_correct.py %f'

This program assumes that the folder structure is that
produced by convert_RAW.py. That is there is a tiff folder
containing the file to be corrected and a summary folder
that is in the same directory as tiff folder.

This program is a python version of Nayoas MATLAB routine.
It is likely to be slightly faster. Note the guaussian blur
ruins the corpeak2 function. corpeak2 is a complicated 
function that uses maths I don't understand. By default 
the gaus produced a 0 matrix in Nayoas code, do I have 
removed the kernel altogether in my implementation. May 
cause havok in the future?
"""

def main(filename):
    
    start = timer()
    
    path, name = os.path.split(filename)
    name = name.split(".")[0]
    path = os.path.split(path)[0]
    summarypath = path + "/summary"
    tiffpath = path + "/tiff"
    
    stack = tifffile.imread(filename)
    
    ll, ww, hh = stack.shape

    tvec = get_translation(stack)
    corrected = correct_motion(stack[1:], tvec)

    np.savetxt("%s/displacement.csv" %path, tvec, 
                        fmt='%3d', 
                        delimiter = ",", 
                        header = "vshift,hshift",
                )
    
    print("\tname: ", name)
    
    plt.plot(tvec[:,0], 'r-', label = 'vertical')
    plt.plot(tvec[:,1], 'b-', label = 'horizontal')
    plt.legend()
    plt.ylabel("displacement (pixels)")
    plt.xlabel("frame")
    plt.title("%s motion correction" %name)
    plt.savefig("%s/displacement.pdf" %summarypath)
     
    fn = "%s/%s_mcavg.tiff" %(tiffpath, name) 
    tifffile.imsave(fn, corrected.mean(axis = 0).astype('uint16'))
    
    fn = "%s/%s_mc.tiff" %(tiffpath, name) 
    stack = np.array(stack).astype('uint16')
    stack[1:] = corrected.astype('uint16')
    tifffile.imsave(fn, stack)
    
    print("\t(%3.5g s)" %(timer()-start))
    
    return corrected
    
def get_translation(stack, template = None, notebook = False, **kwargs):
    
    if notebook:
        pbar = tqdm.tqdm_notebook
    else:
        pbar = tqdm.tqdm
    
    if not template:
        avg = stack.mean(axis = 0)
        f1 = np.fft.fft2(avg)
    else:
        f1 = np.fft.fft2(template)
    
    xx, yy = avg.shape
    
    # cloc gives the x and y values to
    # correctly align the image
    tvec = np.array([corpeak2(frame, (xx,yy), f1) for frame in pbar(stack, **kwargs)])

    return np.array(tvec)

def correct_motion(stack, tvec):
    
    #np.roll is analogous to MATLAB circshift()
    stack = [np.roll(frame, v, axis = 0) for frame, (v, h) in zip(stack, tvec)]
    stack = [np.roll(frame, h, axis = 1) for frame, (v, h) in zip(stack, tvec)]

    # replace the moved edge with NaNs. 
    for i, frame, (v,h) in zip(count(), stack, tvec):
        if v > 0:
            frame[:v,:] = np.nan
        elif v < 0:
            frame[v:,:] = np.nan
    
        if h > 0:
            frame[:, :h] = np.nan
        elif h < 0:
            frame[:, h:] = np.nan
    
        stack[i] = frame
        
    return np.array(stack)
    
def corpeak2(frame, shape, f1 = None):
    
    """
    Returns the vertical and horizontal displacement of frame
    from the best fit of the discrete Fourier transform of avg
    """
    
    xx, yy = shape
    
    # Edge of the movie is not involved in the following calculation
    
    if type(f1) == None:
        f1 = np.fft.fft2(avg)#this is fixed
    
    f2 = np.fft.fft2(frame)

    buf = f1 * np.conj(f2)

    cf = np.fft.ifft2(buf)
    #returns the maximum values of cf along the 0th axis (flatten) and the indicies of those elemenents
    mcf1 = np.max(cf, axis = 0)
    id1 = np.argmax(cf, axis = 0)
    id2 = np.argmax(mcf1)

    if id1[id2] > xx / 2:
        v = id1[id2] - xx
    else:
        v = id1[id2]

    if id2 > yy / 2:
        h = id2 - yy
    else:
        h = id2
    
    return (v, h)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(usage)
    else:
        filename = sys.argv[1]
        
        #avg = tifffile.imread(sys.argv[2])
        
        path, name = os.path.split(filename)
        name = name.split(".")[0]
        path = os.path.split(path)[0]
        summarypath = path + "/summary"

        if not any(['-replace' in arg for arg in sys.argv]):
            if any(['_mc.tiff' in f for f in os.listdir(summarypath)]):
                print("\ttiffs already found")
                quit()

        main(filename)
