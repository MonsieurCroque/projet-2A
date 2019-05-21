# -*- coding: utf-8 -*-
"""
Created on Sat May 18 09:03:13 2019

@author: simon
"""
from math import sqrt

#--------------------Parameters-----------------------------

n = 100 #nb of table values for longitude and latitude
freq = 1 #in Hz
eps = 10 #required precision in meters

#--------------------Program------------------------

varContentArduino = "T = {"
R = 6637813.7

for long in range (n):
    for lat in range (n):
        if sqrt(lat**2+long**2) > 10000000*eps/R:
            varContentArduino += "0, "
        else:
            varContentArduino += "1, "

table = varContentArduino[0:-2] + "}"

print(table)