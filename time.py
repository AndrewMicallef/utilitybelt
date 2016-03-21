import datetime as dt
import numpy as np

def _timedelta(t0, t1):
    """
    uses dummy dates to perform a time 
    delta operation on two times, 

    returns number of seconds in interval
    """

    dummydate = dt.date(2000,1,1)

    try:
        t0 = dt.datetime.combine(dummydate,t0)
        t1 = dt.datetime.combine(dummydate,t1)

        return  (t0 - t1).total_seconds()

    except:
        return np.nan