
def convert_inches(inch):
    '''converts an inch value to a centimeter'''
    CM_PER_INCH = 2.54
    return inch / CM_PER_INCH
    
    
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
