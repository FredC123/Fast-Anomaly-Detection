# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 10:19:20 2022

@author: Fred Coerver

This module takes a pandas frame as input, together with several hyperparameters. 
The pandas data frame must have a straight forward x and y column. Not morem Not less.
The output are two pandas dataframes.
1) table with statistal information of the input and whether a value x is identified as a spike or dip in the
dataset, based on the input parameters. The algorithm makes a window of datapoints from x - windowsizeleft to  x + windowsizeright
Linear regression is performed on this x-range with the give y-values. The regression value : y = slope*x+intercept
This window is iterated over the pandas frame and the regression values are put into the output table, along with the other statistical values
Input dataframe structure :
    1) pandas index as int
    2) x or DateTime value format %Y-%m-%d %H:%M:%S {working on an update that also accepts floats as x}. 
    Columnname must be "DateTime" if Timescale is true and must be next/right to the index
    3) y {float or int}. Columnn name is free. 

The dataframe can have more columns, but the script only analyzes 1 columns at a time.
So in in case you want to analyze more columns, you need to call the script for each column and slicing 
the dataframe in a way that the input frame complies to 1), 2) and 3)

Hyperparameters
ignore_startsamples = 5 (in case you want to omit starting rows from your calculation of the dataset. 
                         This parameter does not delete the rows! = default is 5. 
                         In case you increase the windowsizeleft, you might need to increase this value as well)
ignore_endsamples = 3 (in case you want to omit starting rows from your calculation of the dataset. 
                         This parameter does not delete the rows! 
                         In case you increase the windowsizeright, you might need to increase this value as well)

defaults:
P1inc=10 ()                  ---> In case the standard deviation of a regression window is P1inc-times higher as the previous std, 
                                  then this x value is marked as a spike
accuracy = 4                 ---> If a y-value exceeds the regressed value +- accuracy * std then this x-value is marked as spike
window_sizeleft = 3          ---> the regresssionwindow is #windowsizeleft x-values from the analyzed x-point and #windowsizeright x-values
                                  from the analyzed x-point. So suppose the algorythm calculates whether x[j] is a spike, 
                                  then the window x[j-windowsizeleft] until x[j+windowsizeright] is considerd as the window of x-points.
                                  From these x- an y-point the regression is calculated, and the regression value is compared with the actuel y-value
                                  
window_sizeright = 3         ---> amount of datapoint right from the x-value, which is subject for analyzing whether it is a spike/dip or not
ignoreendsamples = 3         ---> the Endresult output dataframe is capped with [ignorestartsamples:-ignoreendsamples] before returning to main
Timescale                    ---> If x-values are different from time then any string is valid, in case the x-values need to be in timeformat then this parameter is True.



OUTPUT:
1) Pandas dataframe with format columns:
    'DateTime', 'y-value', 'KPI_name', 'Regr_value', 'Value', 'Unixtime',
       'Std', 'spike', 'spikevalue', 'Slope', 'Intercept', 'Diff',
       'Regr_value_plus_std', 'Regr_value_min_std'

2) Pandas dataframe as 1) but then sorted and 'spike' ==1 or ==-1

"""



def Get_SandD(td_local,acc=6,
              windowsizeleft=3,
              windowsizeright=3,
              sp_name="KPI_name",
              P1=10,
              ignorestartsamples=0,
              ignoreendsamples=0,
              Timescale=True):

    #import relevant modules just in case they are not loaded by main
    import pandas as pd
    import numpy as np
    from scipy import stats
    import sys
    import datetime
    import time
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")

    # Return the calculated regression value of the value x , which is the x-value in the mid of the window
    def myfunc(x):
        return slope * x + intercept

    #Convert Dateformat to Unixtime
    def DT2Unix(DT):
        unix = int(time.mktime(datetime.datetime.strptime( DT ,"%Y-%m-%d %H:%M:%S").timetuple()))
        return unix

    # Define the variables, which will be listed in the output pandas frame
    LS = len(td_local)
    #KPIlist = td_local.columns
    #KPIlist = KPIlist[1:].to_list()
    #k=0
    if Timescale == True:
        xas = "Unixtime"
    else:
        xas = td_local.columns.to_list()[0]
    KPI = sp_name
    dfSin = td_local
    #dfSin = dfSin[ignorestartsamples:-ignoreendsamples]
    dfSin["KPI_name"] = sp_name
    dfSin["Regr_value"] = 0.0
    dfSin["Value"] = 0.0
    dfSin["Unixtime"] = 0
    dfSin["Std"] = 1.0
    dfSin["spike"] = 0.0
    dfSin["spikevalue"] = 1.0
    dfSin["Slope"] = 1.0
    dfSin["Intercept"] = 1.0
    dfSin["Diff"] = 1.0
    dfSin["Regr_value_plus_std"] = 1.0
    dfSin["Regr_value_min_std"] = 1.0

    # Fill the Unix time column with the unixtime, so that linear regression is possible of this part of the timetable
    j = 0
    while j<LS and Timescale == True:
        dfSin["Unixtime"][j] = DT2Unix(str(dfSin["DateTime"][j]))
        dfSin["Value"][j] = dfSin[KPI][j]
        j += 1

    j=windowsizeleft
    while j < LS-windowsizeright :
        x = dfSin[xas][j - windowsizeleft:j].to_list() + dfSin[xas][j+1:j + windowsizeright+1].to_list() # regression point before and after RegrValue
        #print(f"x={x}")
        y = dfSin[KPI][j - windowsizeleft:j].to_list() + dfSin[KPI][j+1:j + windowsizeright+1].to_list()
        #print(f"y={y}")
        slope, intercept, r, p, std_err = stats.linregress(x, y)
        #print(f"slope/interept:{slope}/{intercept}")
        mymodel = list(map(myfunc, x))
        dfSin["Regr_value"][j] = slope * dfSin[xas][j] + intercept
        dfSin["Diff"][j] = abs(dfSin[KPI][j] - dfSin["Regr_value"][j])
        dfSin["Slope"][j] = float(slope)
        dfSin["Intercept"][j] = float(intercept)
        dfSin["Std"][j] = (np.array(mymodel) - np.array(y)).std()
        dfSin["Regr_value_plus_std"][j] = slope * dfSin[xas][j] + intercept + acc * dfSin["Std"][j]
        dfSin["Regr_value_min_std"][j] = slope * dfSin[xas][j] + intercept - acc * dfSin["Std"][j]
        if dfSin[KPI][j] > dfSin["Regr_value"][j] + acc*dfSin["Std"][j]: # and dfSin[KPI][j] > 2: 
            dfSin["spike"][j] = 1
        elif dfSin[KPI][j] < dfSin["Regr_value"][j] - acc*dfSin["Std"][j]:
            dfSin["spike"][j] = -1
        elif dfSin["Std"][j] > P1 * dfSin["Std"][j-1]:
            dfSin["spike"][j] = P1
        else:
            pass
        j += 1

    j = 1
    while j < LS:
        if dfSin["spike"][j] != 0:
            dfSin["spikevalue"][j] = dfSin["Regr_value"][j]
        else:
            dfSin["spikevalue"][j] = dfSin[KPI][j]
        j += 1

    if Timescale == True:
        spikelist = pd.concat([dfSin[dfSin["spike"]>=1],dfSin[dfSin["spike"]<=-1]]).sort_values(by="DateTime")
    else:
        spikelist = pd.concat([dfSin[dfSin["spike"]>=1],dfSin[dfSin["spike"]<=-1]]).sort_values(by=xas)
        
    dfSin = dfSin.fillna(0)
    dfSin = dfSin[ignorestartsamples:len(dfSin)-ignoreendsamples]
    #spikelist = spikelist[ignorestartsamples:-ignoreendsamples]
    
    return dfSin, spikelist



