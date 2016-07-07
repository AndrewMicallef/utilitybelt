#1. Capture the Raw image
#
#2. Correct the motion
#   2.5. save the corrected motion tiff 
#   and displacement information
#
#3. Bin the image into 500 ms sums
#   3.5. Save the binned image
#
#6. Draw the ROIs
#7. Save Rois
#8. Measure for all images
#9.

import os
from utilitybelt.ThorImage import thorfile
import motion_correct
import utilitybelt.numerical as numerical
import tifffile as tif
import numpy as np
import matplotlib.pyplot as plt
import sys

if sys.argv[1]:
    inpath = sys.argv[1]
    
    if '-overwrite' in sys.argv:
        overwrite = True
    else:
        overwrite = False
        
else:
    print "needs file"
    quit()

def bin_image(stack, dt):

    dd = len(stack)
    binned_image = [stack[i:i+dt].mean(axis=0)
                        for i in xrange(0, dd, dt)]

    return np.array(binned_image)

'''
housekeeping to get the filename and path
'''
    
path, name = os.path.split(inpath)
summarypath = path + "/summary"
tiffpath = path + "/tiff"
if not os.path.exists(summarypath):
    os.makedirs(summarypath)
if not os.path.exists(tiffpath):
    os.makedirs(tiffpath)

if not overwrite and any(["_mc_1sbin.tiff" in f for f in os.listdir(tiffpath)]):
    print "\t\ttiffs already found"
    quit()    

image = thorfile(path)
name = image.meta['Name']['name']
img = image.stack(0)
image.clear() # this should free the memory of the raw image.

fn = "%s/%s.tiff" %(tiffpath, name) 
tif.imsave(fn, img.astype('uint16'))

'''
-----------------
 
2. Correct motion
-----------------
The first frame typically has the shutter opening, 
for this reason it is excluded from motion correction
'''

img[1:], displacement = motion_correct.correct_motion(img[1:])

#The first frame didn't get touched, so add a nothing value

#plot and save the results
plt.plot(displacement[:,0], 'r-', label = 'vertical')
plt.plot(displacement[:,1], 'b-', label = 'horizontal')
plt.legend()
plt.ylabel("displacement (pixels)")
plt.xlabel("frame")
plt.xlim(0, displacement.shape[0])
plt.title("%s motion correction" %name)
plt.savefig("%s/displacement.pdf" %summarypath)

np.savetxt("%s/displacement.csv" %summarypath, displacement,
                    fmt='%3d', 
                    delimiter = ",", 
                    header = "vshift,hshift",
            )

fn = "%s/%s_mcavg.tiff" %(tiffpath, name) 
tif.imsave(fn, img.mean(axis = 0).astype('uint16'))
    
fn = "%s/%s_mc.tiff" %(tiffpath, name)
tif.imsave(fn, img.astype('uint16'))            

'''
------------------

3. Bin the Images
-----------------
3.1. Extract the frameRate from the thorimage. 
    Thorimage saves the framRate under LSM, 
    in terms of fps. In addition to removing fps, 
    I convert the framerate, first to a number, then 
    to an int so I can use it for indexing later
'''

dt = image.meta['LSM']['frameRate']
dt = dt.split(" fps")[0]
dt = int(numerical.num(dt))

'''
3.2 Return the image in 500 ms bins
'''
img = bin_image(img, dt)

fn = "%s/%s_mc_1sbin.tiff" %(tiffpath, name)
tif.imsave(fn, img.astype('uint16'))