# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 20:42:14 2022

@author: Fred Coerver
"""

import pandas as pd
import numpy as np
from scipy import stats
import sys
import datetime
import time
import matplotlib as plt
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
    
pd.options.display.float_format = '{:,.6f}'.format

#Userdefined module
from fad_v02 import Get_SandD

######################### READ DATA #################################################
td = pd.read_excel("./Testdata_inout2.xlsx",sheet_name="inputdata",usecols="B:C")
writer = pd.ExcelWriter("./Testdata.xlsx")

######################### INITIALIZE DATA   #########################################
kpi_input = td.columns.to_list()
t=1
P1inc=10
accuracy = 4
window_sizeleft = 4
window_sizeright= 4
Time_scale=True
ignore_startsamples = 3 
ignore_endsamples = 3
td_in = td[[kpi_input[0],kpi_input[t]]]

##########################  CALL MODULE   ###########################################
dfSin_gl, spikelist_gl = Get_SandD(td_in,
                                   acc=accuracy,
                                   windowsizeleft=window_sizeleft,
                                   windowsizeright=window_sizeright,
                                   sp_name=kpi_input[t],
                                   P1=P1inc,
                                   ignorestartsamples = ignore_startsamples,
                                   ignoreendsamples = ignore_endsamples,
                                   Timescale=Time_scale
                                   )

##########################    write data to excel   #################################
dfSin_gl.to_excel(writer,sheet_name="Sheet4")  
spikelist_gl.to_excel(writer,sheet_name="Sheet5") 
writer.save()







