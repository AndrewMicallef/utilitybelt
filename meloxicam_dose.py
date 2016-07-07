import sys

usage = """
meloxicam_dose (mass [,units = 'g', fraction = 1.4])
	
returns the volume in mL required for a dose of meloxicam
at using the 5 mg / mL concentrate
"""

def meloxicam_dose(mass, units = 'g'):
    if units == 'g':
        print "\tmass:", mass, 'g'
        mass = float(mass) / 1000
        print "\tmass in kg:", mass, 'kg'
        
    #(3mg / kg) / (5 mg/mL)
    # = 3/5 mL/kg 
	dose = (3 * mass) / 5
	print "\n\t3 mg/kg meloxicam [5mg/mL] dose:\t", dose, "mL"
    
	
	
if __name__ == "__main__":
	try:
		meloxicam_dose(sys.argv[1])
	except:
		print usage