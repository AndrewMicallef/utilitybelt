# coding: utf-8
# Usage `age_today age_in_weeks YYYYMMDD`
# returns age of animal today given it's
# age in weeks on a specific date

import datetime
import sys

def age_today(age, at_date, units = 'weeks'):
	at_date = datetime.datetime.strptime(at_date, "%Y%m%d").date()
	 
	d0 = at_date
	d1 = datetime.date.today()

	delta = d1 - d0

	print delta.days, 'days since', at_date

	exec ("delta = delta + datetime.timedelta(%s=%s)" %(units, age))
	print "age today, P%s" %delta.days
	
	return delta.days

if __name__ == "__main__":
    arg = sys.argv
    age = arg[1]
    at_date = arg[2]
    units = arg[3]
    
    age_today(age, at_date, units= 'weeks')