# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 20:51:23 2019

@author: simon
"""
#--------------------------------libraries-------------------------------------

from random import random
from math import *

#------------------------------auxiliary function------------------------------

# convert (latitude, longitude) to cartesian coordinates
def convertcart(lat,lon):
    
    R=6300000 
    
    x=R*cos(lat*pi/180)*cos(lon*pi/180)
    y=R*cos(lat*pi/180)*sin(lon*pi/180)
    z=R*sin(lat*pi/180)
    
    return(x,y,z)

#give distance between P2 and slope in cartesian
def distancedir(slopePoint1,slopePoint2,point):
    
    a = slopePoint1[0] - slopePoint2[0]
    b = slopePoint1[1] - slopePoint2[1]
    c = slopePoint1[2] - slopePoint2[2]
    
    distanceFunction = lambda x : sqrt((point[0]-(slopePoint2[0] + x*a))**2 + (point[1]-(slopePoint2[1] + x*b))**2 + (point[2]-(slopePoint2[2] + x*c))**2)
    return min([distanceFunction(eps*0.0001) for eps in (range(-10000,1000))])

#give distance between P2 and slope in (latitude, longitude)
def distance(coord0,coord1,coord2):
    
    if (coord1[1]-coord0[1])**2 + (coord1[0]-coord0[0])**2 != 0:
        return abs((coord1[1]-coord0[1])*coord2[0]-(coord1[0]-coord0[0])*coord2[1] + coord1[0]*coord0[1] - coord1[1]*coord0[0])/sqrt((coord1[1]-coord0[1])**2 + (coord1[0]-coord0[0])**2)
    else:
        return 100

#----------------------------data from runtastic gpx---------------------------

txt = """<<metadata>
    <copyright author="www.runtastic.com">
      <year>2019</year>
      <license>http://www.runtastic.com</license>
    </copyright>
    <link href="http://www.runtastic.com">
      <text>runtastic</text>
    </link>
    <time>2019-02-12T18:24:54.000Z</time>
  </metadata>
  <trk>
    <link href="http://www.runtastic.com/sport-sessions/2757080529">
      <text>Cliquez sur ce lien pour voir cette activité sur Runtastic.com</text>
    </link>
    <trkseg>
      <trkpt lon="-1.6339641809463501" lat="48.1323280334472656">
        <ele>120.0</ele>
        <time>2019-02-12T18:24:56.000Z</time>
      </trkpt>
      <trkpt lon="-1.6342105865478516" lat="48.1322822570800781">
        <ele>118.0</ele>
        <time>2019-02-12T18:25:11.000Z</time>
      </trkpt>
      <trkpt lon="-1.6346733570098877" lat="48.1320800781250000">
        <ele>113.0</ele>
        <time>2019-02-12T18:25:34.000Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

# Transform data into array

lonOriginalVect = []
latOriginalVect = []
timeOriginaVect = []

lignVect =  txt.split("\n")

for lign in lignVect:
    afterLonInLignVect =  lign.split('<trkpt lon="')
    
    if len(afterLonInLignVect) > 1:
    
        coordVect = afterLonInLignVect[1].split('" lat="')
        
        lonOriginalVect.append(float(coordVect[0]))
        latOriginalVect.append(float(coordVect[1].split('">')[0]))
    
    afterTimeInLignVect =  lign.split('<time>2019-02-12T18:')
    
    if len(afterTimeInLignVect) > 1:
        
        timeStampVect = (afterTimeInLignVect[1].split(".000Z</time>")[0]).split(":")
        
        timeOriginaVect.append(float(timeStampVect[0])*60+float(timeStampVect[1]))

# Add data points to simulated GPS
    
latSimulatedVect = []
lonSimulatedVect = []

for i in range(1, len(latOriginalVect)):
    
    nbPointAdded = int(random()/1.1*(timeOriginaVect[i] - timeOriginaVect[i-1]))
    
    latSimulatedVect.append(latOriginalVect[i])
    lonSimulatedVect.append(lonOriginalVect[i])
    
    if nbPointAdded > 0:
        
        epsi_lat = (latOriginalVect[i] - latOriginalVect[i-1])/nbPointAdded
        epsi_lon = (lonOriginalVect[i] - lonOriginalVect[i-1])/nbPointAdded
        
        for j in range(nbPointAdded):
            
            latSimulatedVect.append(latOriginalVect[i-1]+epsi_lat*j)
            lonSimulatedVect.append(lonOriginalVect[i-1]+epsi_lon*j)

#----------------------------data from runtastic gpx---------------------------

slopeLonLatPoint1 = (latSimulatedVect[0],lonSimulatedVect[0])
slopeLonLatPoint2 = (latSimulatedVect[1],lonSimulatedVect[1])
lonLatPointInMemory = slopeLonLatPoint1

slopeCartPoint1 = convertcart(slopeLonLatPoint1[0], slopeLonLatPoint1[1])
slopeCartPoint2 = convertcart(slopeLonLatPoint2[0], slopeLonLatPoint2[1])
cartPointInMemory = slopeCartPoint1

latAfterTreatment = [latSimulatedVect[0]]
lonAfterTreatment = [lonSimulatedVect[0]]

for i in range(2, len(latSimulatedVect)):

        newCartPoint = convertcart(latSimulatedVect[i], lonSimulatedVect[i])
        
        if (distancedir(slopeCartPoint1,slopeCartPoint2,newCartPoint) > 10):
            
            latAfterTreatment[-1] = lonLatPointInMemory[0]
            lonAfterTreatment[-1] = lonLatPointInMemory[1]
            
            latAfterTreatment.append(latSimulatedVect[i])
            lonAfterTreatment.append(lonSimulatedVect[i])
            
            slopeLonLatPoint1 = lonLatPointInMemory
            slopeLonLatPoint2 = (latSimulatedVect[i], lonSimulatedVect[i])
            
            cartPointInMemory = cartPointInMemory
            slopeCartPoint1 = cartPointInMemory
            slopeCartPoint2 = newCartPoint
     
        else:
            
            lonLatPointInMemory = (latSimulatedVect[i], lonSimulatedVect[i])

print(latAfterTreatment)
print(lonAfterTreatment)
          