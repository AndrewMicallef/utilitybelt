#python3

import h5py
import datetime
import numpy as np

class wsfile:

    """
    This class holds the wsfile.
    to access the raw h5 use wsfile.f
    
    Updated to handle new file taxonomy sometim after v 0.8
    """
    
    def __init__(self, infile):
        f = h5py.File(infile, 'r')

        self.f = f
                
        if 'VersionString' not in self.f['header']:
            #This is likeley the version 0.801 ws file!
            #Double check this against the new specification
            IsContinuous = 'header/IsContinuous'
            IsTrialBased = 'header/IsTrialBased'
            TrialDuration = 'header/TrialDuration'
            clock = 'header/ClockAtExperimentStart'
        
        else:
            version  = float(self.f['header/VersionString'].value[0])
        
            if version >= 0.915:
                IsContinuous = 'header/AreSweepsContinuous'
                IsTrialBased = 'header/AreSweepsFiniteDuration'
                TrialDuration = 'header/SweepDuration'
                clock = 'header/ClockAtRunStart'


        isActive = f['header/Acquisition/IsChannelActive'].value.astype(bool)
        self.isActive = isActive.reshape(-1)
        
        self.nameslist = f['header/Acquisition/AnalogChannelNames'].value[self.isActive]
        
        unitslist = f['header/Acquisition/AnalogChannelUnits'].value[self.isActive]
        self.unitslist = {name:units for name, units in zip(self.nameslist, unitslist)}
        self.IsContinuous = bool(f[IsContinuous].value.item())
        self.IsTrialBased = bool(f[IsTrialBased].value.item())
        self.TrialDuration = f[TrialDuration].value.item()
        self.SampleRate = f['header/Acquisition/SampleRate'].value.item()
        
        dstamp = f[clock].value
        self.dstamp = datetime.datetime(*dstamp)      
        
        trace_times = []
        for group in f:
            if group != u'header':
                trigtime = f['%s/timestamp' %group].value.item(0)

                delta = datetime.timedelta(0, int(trigtime)) #lossy, but acceptable given time resolution            
                trace_times.append( (self.dstamp + delta) )
        
        self.timestamp = np.array(trace_times)
    
        
    def data(self):
        """
        
        returns the h5 data as a dictionary of numpy arrays.
        index by data[channel name] = np.array(trial x samples])
        
        """
    
        analogDATA = {} #tmp list to hold the analog data
        
        for group in self.f:
            if group != u'header':
                for n in range(len(self.nameslist)):
                    trace = self.f['%s/analogScans' %group].value[n].astype('float')
                    trace = (np.array(trace) * (20.0 / 2**16))
            
                    try:  
                        analogDATA[self.nameslist[n]].append(trace)
                    except KeyError:
                        analogDATA[self.nameslist[n]] = [trace]
                        
        
        for k in analogDATA:
            analogDATA[k] =  np.array(analogDATA[k])
            
        return analogDATA
        
    def close(self):
        self.f.close()

def sort_dict(dict, by):
    """
    sorts the dictionary entries by the entry given
    """
    
    by_index = dict.keys().index(by)
    
    tmp = zip(*[(dict[k]) for k in dict])
    tmp = sorted(tmp, key = lambda x: x[by_index])
    tmp = zip(*tmp)

    return {k: v for k, v in zip(dict.keys(), tmp)}

def concact_data(files, skip_continuous = True):

    """
    Takes a list of wavesurfer files and merges all 
    data into a single dictionary of numpy arrays
    
    UPDATE: can handle concactantion of files with 
            different channel names
    """

    data = {'trigger' : [], 'WSfilename': [],}

    for file in files:
        name = file.split("/")[-1]
        ws = wsfile(file)


        if ws.IsContinuous and skip_continuous:
            continue

        trial_data = ws.data()
        ws.close()

        for k in trial_data:
            try:
                data[k].append(trial_data[k][0:])
            except KeyError:
                data[k] = [trial_data[k][0:]]

        shape = trial_data[k][0:].shape

        #This is to compensate for files with different channel names
        for k in data:
            if k in ("trigger", "WSfilename"):
                continue
            if k not in trial_data.keys():
                data[k].append(np.zeros(shape)*np.nan)

        for t in ws.timestamp:
            data['trigger'].append(t.time())
            data['WSfilename'].append(name)

    for k in data:
        if k in ("trigger", "WSfilename"):
            continue
        data[k] = np.array([t for i in data[k] for t in i])
        
    return data