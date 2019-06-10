#--------------------------------libraries-------------------------------------

import numpy

# for interpolation
import scipy.optimize as scimin

# for plotting
import matplotlib.pyplot as plt

# for background map
from mpl_toolkits.basemap import Basemap

import bluetooth

#----------------------------data from ESP32-----------------------------------

#Get data from ESP32

hostMACAddress = '30:ae:a4:8f:f0:de' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.    
port = 7

s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.connect((hostMACAddress, port))

i = 0
newData ="t"
dataAcc = []

while i < 5:
    while newData != "":
        newData = raw_input()
        dataAcc.append(newData)
    
    print("received [%s]" % newData)
    
    i+=1
    
client_socket.close()
server_socket.close()

# Transform data into array

dataLong = numpy.array([dataAcc[2*i] for i in range(int(len(dataAcc)/2))])
dataLat = numpy.array([dataAcc[2*i + 1] for i in range(int((len(dataAcc) - 1)/2))])

#-----------------------------data for testing---------------------------------

#Gathered in Rennes during a 2 min bus ride thanks to Runtastic

#dataLong = numpy.array([-1.647416  , -1.64801121, -1.64863586, -1.6492945 , -1.64979613,
#       -1.65033984, -1.65089107, -1.65147328, -1.65207493, -1.65266132,
#       -1.65324414, -1.65381372, -1.65437889, -1.65497065, -1.65551889,
#       -1.65614533, -1.65629029, -1.65629029])
#dataLat = numpy.array([48.1114006 , 48.11125565, 48.1111145 , 48.11100602, 48.1108284 ,
#       48.11069489, 48.11056519, 48.11043167, 48.11032104, 48.11023712,
#       48.11015701, 48.11010742, 48.11008835, 48.11009598, 48.11009216,
#       48.11008072, 48.1100769 , 48.1100769 ])

#---------------------nterpolation (LS without constraints)--------------------

# model for fit

def fitfunc(x,p): #f(x)= a x^2 + b x+ c
    a,b,c=p
    return c + b*x + a*x**2

# array of residuals

def residuals(p): 
    return abs(dataLatTest-fitfunc(dataLongTest,p))

 # function we want to minimize

def sum_residuals_custom(p):
    return sum(residuals(p)**2)

# interpolation

def interpolation(n, epsilon, x, y):
    
    global dataLongTest # dataset for interpolation
    global dataLatTest
    dataLongTest = x[0:3]
    dataLatTest = y[0:3]
    
    p0=[1,0,0] # initial parameters guess
    p,cov,infodict,mesg,ier = scimin.leastsq(residuals, p0,full_output=True) #interpolation
    
    curve_interpolation = [p] # add model to result
    curve_points = [x[0]]
    i = 0
    
    while i < n :
        
        if abs(fitfunc(x[i],p) - y[i]) > epsilon:
            
            dataLongTest = x[(i-2):(i+2)]
            dataLatTest = y[(i-2):(i+2)]
            dataLatTest[0] = fitfunc(x[i-2],p)
            
            p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
            pwith=scimin.fmin_slsqp(sum_residuals_custom,p)
            
            curve_interpolation.append(pwith)
            curve_points.append(x[i-2])
            i += 1
            
        i+=1
    
    curve_points.append(x[n-1]) # add last point 
    
    return curve_interpolation, curve_points


#----------------------------------plotting------------------------------------

# adding background map

latMin = min(dataLat) - 0.0005 # background map size
latMax = max(dataLat) + 0.0005
longMin = min(dataLong) - (latMax - latMin)/2
longMax = max(dataLong) + (latMax - latMin)/2

m = Basemap(llcrnrlon=longMin, llcrnrlat= latMin, urcrnrlon=longMax, urcrnrlat=latMax, epsg = 4326,resolution='i',projection='merc')
m.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 12000, verbose= True)

# adding GPS coordinates

m.plot(dataLong,dataLat,ls="",marker="x",color="red",mew=2.0,label="Datas")

#adding path

curve_interpolation, curve_points = interpolation(len(dataLong),0.0001, dataLong, dataLat)

for e in range(len(dataLong)-1):
    morex=numpy.linspace(dataLong[e],dataLong[e+1], num = 500, endpoint = True)
    morey = numpy.linspace(dataLat[e],dataLat[e+1], num = 500, endpoint = True)
    m.plot(morex,morey,color="blue")

plt.show()
