import numpy as np
import math

def get_events_ind(trace, threshold, base):
    """
    Finds parts of the trace that cross the the threshold,
    then scans backwards and forwards to get the times that
    the event is above baseline.
    
    returns a 2d array of start,stop indexes
    """
    base_up = (trace > base)

    base_diff = np.diff(base_up.astype(int))
    edges = [(v, i) for i,v in enumerate(base_diff) if v]

    if edges[0][0] == -1: 
        edges.insert(0, (1,0))    
    if edges[-1][0] == 1:
        edges.append((-1,-1))

    edges = np.array(edges).transpose()[1]
    edges = edges.reshape(-1, 2)

    events = [(st, ed) for st, ed in edges 
                    if (trace[st:ed] > threshold).any()]

    return np.array(events)

def get_trial_start_from_stim(stimarr, threshold, bin, dt):
    
    """
    Returns a 1d array corresponding to the indicies of
    each of the first stimuli in a trial. 
    
    stimarr   -- a numpy array of the continuous stimulus data
    threshold -- the threshold to use to determine if a stimulus occured,
                 NOTE: The stimulus gets mean filtered, so use a lower
                 threshold than you might expect. For the speaker I have
                 found 0.5 works niceley.
    bin       -- bin width for downsampling. 500 works well for Speaker
                 Much higher is necessary for the Somatosensory stimulus
    dt        -- The sampling frequency             
                 
    Assumes two sequential stimuli that have a duration
    of 500 ms and are spaced no more than 250 ms apart
    NOTE: will need modification for somatosensory stimulus
    """

    # 1. get the rising edges of the stimulus
    # 2. downsample the rsing edges
    # 3. capture the indicies of blocks oabove threshold    

    stim = edges(stimarr, 0.5)[0]
    dd_stim = downsample(stim, bin, np.mean)  
    stim_ind = get_events_ind(dd_stim, threshold, 0.01)
    '''
    This code takes a high frequency series of spikes
    and effectivley merges it into a single block of activity
    that remains above threshold while the stimulus is on.
    stim_ind is a 2d array of the form (start_index, stop_index)
    for each *event* of the stimulus being on.
    '''
    
    trials = []
    for i, (t0, t1) in enumerate(stim_ind):
    
        # time between start and end of this pulse
        delta_t = (t1 - t0) #in samples!
        
        # comparison to number of samples I would expect 
        # in a 500 ms block of stimulus.
        if (delta_t > 0.4/bin*dt) and (delta_t < 0.6/bin*dt):
            trials.append(t0)
    
    trials = np.array(trials) * bin
    # trials is a 1d list of the start points of all events that
    # are likely to be a stimulus. It gets multplied by bin
    # to convert back to units of the number of samples in
    # raw data.
    

    # because there are two sequential stimuli
    # my trials will have duplicates. To get rid of
    # duplicates I take each start time, and check 
    # the time of the first threshold crossing up to
    # 1.5 seconds prior to the current start time.
    # This gives me a list of indicies alligned to the
    # onset of the first stim.

    trial_onset = []
    for t0 in trials:
        
        onset = (t0-1*dt) + np.argmax(stim[t0-(1*dt):])
        trial_onset.append(onset)
    
    trial_onset = np.array(trial_onset)
    trials = np.unique(trial_onset)
    
    return trials

def partition_data(data, trials, t_offset = (-1,5), dt = 20000):
    """
    Given a dictionary of multiple data channels, each with a
    continuous array of data, split into trials based on the
    list of trial indices
    
    returns a dictionary with each channel.
    
    Keyword arguments
    t_offset -- default (-1,5), a pair of times definming the
                time window to cast around the onset of the stimulus.
                By default captures 1 second before, to 5 seconds after
                
    """
    
    trial_data = {k:[] for k in data.keys()}

    t0, t1 = t_offset
    
    for i, k in enumerate(data):        
        for j, start in enumerate(trials):

            if j:
                trial = data[k][0, start + t0*dt:start + t1 *dt]
                
                if len(trial):
                    trial_data[k].append(trial)
                else:
                    trial_data[k].append(np.zeros((t1-t0)*dt)*np.nan)
                            
        trial_data[k] = np.array(trial_data[k])

    for k, v in trial_data.iteritems():
        print k, len(v)

    return trial_data

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
        
def downsample (a, R, method = np.nanmean):
        """
        bins input array 'a' into chunks of 'R' samples
        """
        pad_size = math.ceil(float(a.size)/R)*R - a.size
        b_padded = np.append(a, np.zeros(pad_size)*np.NaN)

        return method(b_padded.reshape(-1,R), axis=1)