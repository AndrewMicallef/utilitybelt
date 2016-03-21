
# coding: utf-8

# In[14]:


from IPython.display import display, HTML

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages

import os
import datetime

from PIL import Image
import tifffile

from utilitybelt.ws import wsfile
from utilitybelt.ThorImage import thorfile
#get_ipython().magic(u'matplotlib inline')


###dfinitions

def plot_flatten(stack, pdf, method = np.max):
    fig= plt.figure()
    
    fig.suptitle("T - projection")
    plt.imshow(
                method(stack, axis = 0), 
               vmax = np.percentile(stack, 100),
              )
    plt.axis('off')
    pdf.savefig()
    plt.close()
    
def  plot_subbackground(stack, background, pdf, method = np.max):
    fig = plt.figure()
    
    stack =  stack - background
    
    plt.imshow(
        stack_b.max(axis=0), 
        vmax = np.percentile(stack, 100))
    plt.title("stack minus background")
    plt.axis('off')
    pdf.savefig()
    plt.close()

def plot_F0(stack, depth, pdf):
    
    fig = plt.figure()
    f0 = np.mean(stack[:depth], axis = 0)
    
    plt.imshow(f0, vmax = np.percentile(f0, 99.6))
    plt.title("F0\nfirst %d frames" %depth)
    plt.axis('off')

    pdf.savefig()
    plt.close()
    
def plot_Fbackground(fb, time, roi_b, pdf, method = np.max):
    """
    fb : an numpy array of floursence over time in background regions
    roi_b : full path names of background rois used. 
            * Expects a .tiff ending!
            * and looks for a .txt file of the same name!
    
    """
    fig, ax = plt.subplots(1,2)

    ax[1].imshow(method(stack, axis=0), 
                 vmax=np.percentile(stack, 100),
                )
    ax[1].set_title("stack (max intensity )")
    ax[1].axis('off')

    for b, fname in enumerate(roi_b):
        label = fname.split("/")[-1].split(".")[0]

        ax[0].plot(time, fb[b], 
                 c = plt.cm.gnuplot(float(b)/len(roi_b)),
                 label = label,
                 alpha = 0.9,
                )

        fname = fname.replace(".tiff", ".txt")

        tmp = np.loadtxt(fname)
        x,y = tmp.transpose()
        ax[1].plot(x,y, c = plt.cm.gnuplot(float(b)/len(roi_b)))

    ax[0].text(0.5,1,
             "mean background flouresence: %3.5g" %np.mean(fb),
            ha = 'center',
            va = 'bottom',
            weight = 'heavy',
            transform = ax[0].transAxes,
            )
    
    fig.suptitle("background estimation")
    pdf.savefig()
    plt.close()

def plot_Fvtime(F, time, rois, pdf, ylabel = "F"):
   
    for b, label in enumerate(rois):

        tmp = tifffile.imread(label).astype(bool)

        label = label.split("/")[-1].split(".")[0]
        
        fig, ax = plt.subplots(1,2, dpi=300)

        ax[0].plot(time,
                 F[b], 
                 c = plt.cm.gnuplot(float(b)/len(roi_d)),
                 label = label,
                 alpha = 0.9,
                )

        y0,y1 = (F.min(), F.max())

        ax[0].vlines(time[30], y0, y1, label = "f0")
        ax[0].vlines(2, y0, y1, 'g' ,label = "stimulus 0")
        ax[0].vlines(3.5, y0, y1, 'g', label = "stimulus 1")

        ax[0].set_xlabel("time (s)")
        ax[0].set_ylabel(ylabel)

        masked_array = np.ma.masked_where(tmp==0,tmp)

        ax[1].set_title("max intensity projection")
        ax[1].imshow(stack.max(axis=0),)
        ax[1].imshow(masked_array, cmap = plt.cm.gray_r)
        ax[1].axis('off')

        fig.suptitle(r"%s %s" %(ylabel, label))

        #

        #ax[0].legend(loc = 'center left', 
        #           bbox_to_anchor=(1,0.5),
        #          title = "ROI",
        #          )

        pdf.savefig()
        plt.close()
    


###

date = 160128
basepath = "../%s/FOVs/ROI001/" %date

impaths = [
        basepath+p+'/' 
            for p in os.listdir(basepath) 
                if p !='ROIs' 
                    if 'ROIs' in os.listdir(basepath+p+'/tiff')
        ]


for impath in impaths:
    
    if not os.path.exists(impath + impath.split("/")[0] +'.pdf'):
    
        #impath = "../160128/FOVs/ROI001/83_ROI001_d132_0011/"

        img = thorfile(impath)
        stack = img.stack(0)
        
        depth = 30
        

        ROIdirs = (
                impath + "tiff/ROIs/",
                #"../160128/FOVs/ROI001/83_ROI001_d132_0030/tiff/ROIs/",
                #"../160128/83_ROI001_Z[0-400]_0030/tiff/ROIs/",
        )

        rois = []
        for ROIdir in ROIdirs:
            rois.append([ROIdir+r for r in os.listdir(ROIdir) if ".tiff" in r])

        rois = [val for sublist in rois for val in sublist]

        ROI = {}
        for roi in rois:
            ROI[roi] = (tifffile.imread(roi).astype(bool))


        #r = np.max(r, axis = 0)
        #print "the ROIs"
        #plt.imshow(r, cmap=plt.cm.gray)


        fb = np.array([np.mean(stack[:,ROI[roi]], axis = 1) for roi in ROI if "background" in roi])

        roi_b = [r for r in ROI.keys() if "background" in r]

        
        background = np.mean(fb)

        
        f0 = np.mean(stack[:depth], axis = 0)

        time = np.linspace(0,20, 600)

        with PdfPages(impath + impath.split("/")[0] +'.pdf') as pdf:

            #####
            plot_flatten(stack, pdf)
            
            ######
            plot_subbackground(stack, background, pdf)

            ######
            plot_F0(stack, depth, pdf)
            
            #######
            plot_Fbackground(fb, time, roi_b, pdf)
            
            for roi_type in ("dend", "soma"):
            
                #### Florescence figures

                F_abs = np.array([ np.mean(stack[:,ROI[roi]], axis=1) for roi in ROI if roi_type in roi])
                
                F_delta = np.array([(f - np.mean(f[:depth]))/ np.mean(f[:depth]) for f in F_abs])
                
                roifiles = [r for r in ROI.keys() if roi_type in r]
                
                plot_Fvtime(F_abs, time, roifiles, pdf, ylabel = "F")
                
                plot_Fvtime(F_delta, time, roifiles, pdf, ylabel = r"$\frac{F - F_0}{F_0}$")
        


