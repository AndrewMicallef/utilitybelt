#python3

import h5py
import datetime
import numpy as np

class wsfile:

    """
    This class holds the wsfile.
    to access the raw h5 use wsfile.f
    """
    
    def __init__(self, infile):
        f = h5py.File(infile, 'r')

        self.f = f
        
        try:
            f['header/VersionString'].value.astype(float).item() == 0.915
        
                
            IsContinuous = 'header/AreSweepsContinuous'
            IsTrialBased = 'header/AreSweepsFiniteDuration'
            TrialDuration = 'header/SweepDuration'
            Clock = 'header/ClockAtRunStart'
        
        except:
            IsContinuous = 'header/IsContinuous'
            IsTrialBased = 'header/IsTrialBased'
            TrialDuration = 'header/TrialDuration'
            Clock = 'header/ClockAtExperimentStart'
            
        self.IsContinuous = bool(f[IsContinuous].value.item())
        self.IsTrialBased = bool(f[IsTrialBased].value.item())
        self.TrialDuration = f[TrialDuration].value.item()
            
        isActive = f['header/Acquisition/IsChannelActive'].value.astype(bool)
        self.isActive = isActive.reshape(-1)
        
        self.SampleRate = f['header/Acquisition/SampleRate'].value.item()
        self.nameslist = f['header/Acquisition/AnalogChannelNames'].value[self.isActive]
        self.unitslist = f['header/Acquisition/AnalogChannelUnits'].value[self.isActive]

        """
        Aqcuisition variables:
        
        AbsoluteProtocolFileName
        AbsoluteUserSettingsFileName
        Acquisition
        ClockAtExperimentStart
        Display
        Ephys
        ExperimentCompletedTrialCount
        ExperimentTrialCount
        FastProtocols
        HasUserSpecifiedProtocolFileName
        HasUserSpecifiedUserSettingsFileName
        IndexOfSelectedFastProtocol
        IsContinuous
        IsReady
        IsTrialBased
        IsYokedToScanImage
        Logging
        NFastProtocols
        NTimesSamplesAcquiredCalledSinceExperimentStart
        State
        Stimulation
        TrialDuration
        Triggering
        UserFunctions
        """
        
        
        dstamp = f[Clock].value
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
    by_index = dict.keys().index(by)
    
    tmp = zip(*[(dict[k]) for k in dict])
    tmp = sorted(tmp, key = lambda x: x[by_index])
    tmp = zip(*tmp)

    return {k: v for k, v in zip(dict.keys(), tmp)}

def concact_data(files, skip_continuous = True):
    """
    Takes a list of wavesurfer files and merges all 
    data into a single dictionary of numpy arrays
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
                data[k].append(trial_data[k])
            except KeyError:
                data[k] = [trial_data[k]]
        
        for t in ws.timestamp:
            data['trigger'].append(t.time())
            data['WSfilename'].append(name)
        
    for k in data:
        if k in ("trigger", "WSfilename"):
            continue
        data[k] = np.array([t for i in data[k] for t in i])
        
    return data