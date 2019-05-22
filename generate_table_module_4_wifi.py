# -*- coding: utf-8 -*-
"""
Created on Sat May 18 09:03:13 2019

@author: simon
"""
from math import sqrt

#--------------------Parameters-----------------------

n = 100 #nb of table values for longitude and latitude
freq = 1 #in Hz
eps = 0.0001 #required precision for output float

#--------------------To cap float precision-----------

def rounder(value, precision):
    return str(round(value/precision)*precision)

#--------------------Program-------------------------

varContentArduino = "T = {"
R = 6637813.7

for long in range (n):
    for lat in range (n):
        varContentArduino += rounder(1/sqrt((R*long/10000000)**2 + (R*(lat+1)/10000000)**2), eps)  + ", "

table = varContentArduino[0:-2] + "};"

print(table)