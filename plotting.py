import numpy as np
import matplotlib.pyplot as plt

def convert_inches(inches):
    '''converts an inch value to a centimeter'''

    CM_PER_INCH = 2.54
    inches = np.array(inches)
    
    return inches * CM_PER_INCH
    
    
def raster_duration(array, start_trial = 0, ax = None, label = '', **kwargs):
    
    '''Given a 3D list of on - off times in the form (trial x event x time)
       plots a raster on a matplotlib axis.
       Requires matplotlib to be imported and a plot to exist.'''
    
    if ax is None:
        ax = plt.gca()
    
    for i, (t) in enumerate(array, start_trial):
        for j, (up, down) in enumerate(zip(t[::2], t[1::2])):
            ax.hlines(i + 0.5, up, down, 
                      label = label if i + j == start_trial else '',
                      **kwargs)

def plot_raster(stim, lick, water,  
                start_trail = 0,
                axes = plt.gca(),
                start_trial = 0,
                dt = 20000,
               ):

    hit, miss, CR, FA = False, False, False, False
    
    for i, (s, l, w) in enumerate(zip(stim, lick, water), start_trial):

        # stimulus        
        if (s).nonzero()[0].any():
            axes.hlines(i + 0.5, *(s).nonzero()[0]/dt, 
                       color = 'mediumpurple', 
                       lw = 2,
                       label = 'Stimulus' if not i else '',
                      );

        # all licks
        axes.vlines((l).nonzero()[0]/dt, i, i+1, 
                   color = 'lightsalmon',
                   label = 'licks' if not i else '',
                  );
        
        # water valve
        axes.vlines((w).nonzero()[0]/dt, i, i+1, 
                   color = 'RoyalBlue', 
                   lw = 2,
                   label = 'Water valve' if not i else '',              
                  );

    axes.set_ylim(0,i+1);
    axes.set_ylabel('trial');
    axes.set_xlabel('time (s)');
    