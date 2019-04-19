import numpy
import scipy.optimize as scimin
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from random import random
from math import sqrt, log, sin, pi, floor, ceil
from bluetooth import *

# Get data from ESP32
"""
server_socket=BluetoothSocket( RFCOMM )
server_socket.bind(("", 3 ))
server_socket.listen(1)
client_socket, address = server_socket.accept()
dataAcc = ""
while True:
    newData = client_socket.recv(1024)
    if len(newData) == 0:
        break
    dataAcc += newData

print("received [%s]" % dataAcc)

client_socket.close()
server_socket.close()

# Transform data into array

dataLong = numpy.array([dataAcc[2*i] for i in range(floor(len(dataAcc) / 2))])
dataLat = numpy.array([dataAcc[2*i + 1] for i in range(ceil(len(dataAcc) / 2)-1)])"""

# Generate data for testing (Paris)

def generate(n):
    dataLong = numpy.array([2.346033*(1 + sqrt(i+1)/1000) for i in range(n)])
    dataLat = numpy.array([48.850447*(1 + sqrt(i)*(random() -0.5)/100000) for i in range(int(n/2))] + [48.850447*(1 + (sqrt(int(n/2))+log(i+1)**2)*(random() -0.5)/100000) for i in range(n-int(n/2))])
    return dataLong, dataLat

# least square fit without constraints
# Possible to change model
def fitfunc(x,p): # model $f(x)=a x^2+b x+c
    a,b,c=p
    return c + b*x + a*x**2

def residuals(p): # array of residuals
    return abs(dataLatTest-fitfunc(dataLongTest,p))

def interpolation(n, epsilon):
    global dataLongTest
    global dataLatTest
    p0=[1,0,0] # initial parameters guess
    dataLongTest = dataLong[0:3]
    dataLatTest = dataLat[0:3]
    p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
    curve_interpolation = [p]
    curve_points = [dataLong[0]]
    acc=3
    prec = 0
    i=4
    while i < n :
        if abs(fitfunc(dataLong[i],p) - dataLat[i]) > epsilon:
            dataLongTest = dataLong[(i-2):(i+2)]
            dataLatTest = dataLat[(i-2):(i+2)]
            dataLatTest[0] = fitfunc(dataLong[i-2],p)
            p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
            pwith=scimin.fmin_slsqp(sum_residuals_custom,p)
            curve_interpolation.append(pwith)
            curve_points.append(dataLong[i-2])
            acc=3
            prec = i - 2
            i+=1
        else:
            if acc%5 == 0:
                dataLatTest = dataLat[prec:i]
                dataLongTest = dataLong[prec:i]
                dataLatTest[0] = fitfunc(dataLong[i-2],p)
                p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
                curve_interpolation[-1]=p
        acc+=1
        i+=1
    curve_points.append(dataLong[n-1])
    return curve_interpolation, curve_points


def sum_residuals_custom(p): # the function we want to minimize
    return sum(residuals(p)**2)

dataLong, dataLat = generate(50) # comment this if you use vect
curve_interpolation, curve_points = interpolation(len(dataLong),0.0005)

# plotting
# adding background map

latMin = min(dataLat) - 0.0001
latMax = max(dataLat) + 0.0001
longMin = min(dataLong) - (latMax - latMin)/2
longMax = max(dataLong) + (latMax - latMin)/2

m = Basemap(llcrnrlon=longMin, llcrnrlat= latMin, urcrnrlon=longMax, urcrnrlat=latMax, epsg = 4326,resolution='i',projection='merc')
m.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 12000, verbose= True)

# adding GPS coordinates

m.plot(dataLong,dataLat,ls="",marker="x",color="blue",mew=2.0,label="Datas")

# plotting different regression

for e in range(len(curve_points)-1):
    morex=numpy.linspace(min(curve_points[e:e+2]),max(curve_points[e:e+2]), num = 500, endpoint = True)
    m.plot(morex,fitfunc(morex,curve_interpolation[e]),color="red")

# show

plt.show()
