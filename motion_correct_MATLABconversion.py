import os
import numpy as np
import matplotlib.pyplot as plt
import tifffile
import scipy.stats as st
from timeit import default_timer as timer

import sys

usage = """motion_correction.py filename

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

def gkern(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel array."""

    interval = (2*nsig+1.)/(kernlen)
    x = np.linspace(-nsig-interval/2., nsig+interval/2., kernlen+1)
    kern1d = np.diff(st.norm.cdf(x))
    kernel_raw = np.sqrt(np.outer(kern1d, kern1d))
    kernel = kernel_raw/kernel_raw.sum()
    return kernel

def correct_motion(filename):
    
    name = os.path.split(filename)[-1].split(".")[0]
    path = "/".join(filename.split("/")[:-2])
    summarypath = path + "/summary"
    
    stack = tifffile.imread(filename)

    ll, ww, hh = stack.shape

    # this should be a gaussian blur, in fact it results in a zero matrix
    #kernel = gkern(hh)
    #kernel = np.fft.fft2(kernel)
    kernel = []

    corrected, cloc = cor_mot(stack, kernel)
    print "\tname: ", filename,
        
    #save the results
    plt.plot(cloc[:,0], 'r-', label = 'vertical')
    plt.plot(cloc[:,1], 'b-', label = 'horizontal')
    plt.legend()
    plt.ylabel("displacement (pixels)")
    plt.xlabel("frame")
    plt.title("%s motion correction" %name)
    plt.savefig("%s/displacement.pdf" %summarypath)
    
    np.savetxt("%s/displacement.csv", cloc, 
                        fmt='%3d', 
                        delimiter = ",", 
                        header = "vshift,hshift",
                )
     
    fn = "%s/%s_mcavg.tiff" %(summarypath, name) 
    tifffile.imsave(fn, corrected.mean(axis = 0).astype('uint16'))
    
    fn = "%s/%s_mc.tiff" %(summarypath, name) 
    tifffile.imsave(fn, corrected.astype('uint16'))

def cor_mot(stack):

    avg = stack.mean(axis = 0)
    
    print "correlating peaks...",
    start = timer()
    cloc = np.array([corpeak2(avg, frame) for frame in stack])
    print "...correlated peaks (%5.1 s)" %timer() - start 
    
    print "restacking...",
    start = timer()
    #np.roll is analogous to MATLAB circshift()
    stack = [np.roll(frame, v, axis = 0) for frame, (v, h) in zip(stack, cloc)]
    stack = [np.roll(frame, h, axis = 1) for frame, (v, h) in zip(stack, cloc)]
    stack = np.array(stack)  
    print "...restacked (%5.1 s)" %timer() - start
    
    return (stack, cloc)

def corpeak2(avg, frame):

    m, n = avg.shape
    
    # Edge of the movie is not involved in the following calculation
    avg = avg[:, 32:-32]
    frame = frame[:, 32:-32] 
    n = n - 64

    f1 = np.fft.fft2(avg)
    f2 = np.fft.fft2(frame)

    buf = f1 * np.conj(f2)
    
    cf = np.fft.ifft2(buf)
    #returns the maximum values of cf along the 0th axis (flatten) and the indicies of those elemenents
    mcf1 = np.max(cf, axis = 0)
    id1 = np.argmax(cf, axis = 0)
    id2 = np.argmax(mcf1)

    if id1[id2] > m / 2:
        v = id1[id2] - m
    else:
        v = id1[id2]

    if id2 > n / 2:
        h = id2 - n
    else:
        h = id2
    
    return (v, h)

if __name__ == "__main__":
	if sys.argv < 2:
		print usage
	else:
		filename = sys.argv[1]
		
		name = os.path.split(filename)[-1].split(".")[0]
		path = "/".join(filename.split("/")[:-2])
		summarypath = path + "/summary"
		
		if any(['_mc.tiff' in f 
				for f in os.listdir(summarypath)]):
			print "\ttiffs already found"
			quit()
			
		correct_motion(filename)
