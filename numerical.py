import numpy as np
import math


def downsample2D(myarr, factor, estimator=np.mean):
    """
    Downsample a 2D array by averaging over *factor* pixels 
    in each axis. Crops upper edge if the shape is not a 
    multiple of factor.

    This code is pure numpy and should be fast.

    keywords:
        estimator - default to mean.  You can downsample by 
        summing or something else if you want a different 
        estimator
            (e.g., downsampling error: you want to sum & 
         divide by sqrt(n))
    """
    ys,xs = myarr.shape
    crarr = myarr[:ys-(ys % int(factor)),:xs-(xs % int(factor))]
    dsarr = estimator( np.concatenate([[crarr[i::factor,j::factor] 
        for i in range(factor)] 
        for j in range(factor)]), axis=0)
    return dsarr

    
def downsample (a, R, method = np.nanmean):
        """
        bins input array 'a' into chunks of 'R' samples
        """
        pad_size = math.ceil(float(a.size)/R)*R - a.size
        b_padded = np.append(a, np.zeros(pad_size)*np.NaN)

        return method(b_padded.reshape(-1,R), axis=1)


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
    
def get_spikes (array, threshold, smooth_radius = 500, digitise = 75):
    """
    returns the rising edges of the array, 
    after smoothing and digitising
    """
    
    smoothed = moving_average(array, smooth_radius)
    downsampled = downsample(smoothed, digitise)
    thresholded = (downsampled > threshold).astype(int)
    return np.diff(thresholded) == 1

def edges(trace, threshold, type = 'rising'):
    """
    returns a boolean array that is true at the thresholded edges.
    By default returns the rising edge, can take falling edge as well
    """
    
    edge = {'rising':1, 'falling':-1}
    thresholded = (trace > threshold).astype(int)
    
    if type not 'both':
        return np.diff(thresholded == edge[type])
    else:
        return np.diff(thresholded)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
    
    
def edges(trace, threshold, type = 'rising'):
    """
    returns a boolean array that is true at the thresholded edges.
    By default returns the rising edge, can take falling edge as well
    """
    
    edge = {'rising':1, 'falling':-1}
    thresholded = (trace > threshold).astype(int)
    
    if type is not 'both':
        return np.diff(thresholded == edge[type])
    else:
        return np.diff(thresholded)    