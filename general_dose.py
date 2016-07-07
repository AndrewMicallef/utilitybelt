

import sys

usage = """
urethane_dose (mass [,units = 'g', fraction = 1.4])
	
returns the volume in mL required for a dose of urethane
at 1.5 mg / g and 1.6 mg / g.
"""

def urethane_dose(mass, units = 'g', fraction = 1.4):
    if units == 'g':
        print "mass:", mass, 'g'
        mass = float(mass) / 1000
        print "mass in kg:", mass, 'kg'
	dose = (1.4 * mass) / 0.2
	print "1.4 mg/g 20\% urethane dose:", dose, "mL"
	dose = (1.6 * mass) / 0.2
	print "1.6 mg/g 20\% urethane dose:", dose, "mL"
	
	if fraction != 1.4:
		dose = (fraction * mass) / 0.2
		print "%s mg/g 20\% urethane dose:" %fraction, dose, "mL"

if __name__ == "__main__":
	try:
		urethane_dose(sys.argv[1])
	except:
		print usage