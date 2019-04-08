import numpy
import scipy.optimize as scimin
import matplotlib.pyplot as mpl
from random import random
from math import sqrt, log, sin, pi

# Two ways to generate input

#Generates function
def generate(n):
    datax = numpy.array([sin(i*2*pi/25) + random() -0.5 for i in range(n)])
    datay = numpy.array([(sqrt(i) + random() -0.5) for i in range(int(n/2))] + [(sqrt(int(n/2))+log(i+1)**2+ random() -0.5) for i in range(n-int(n/2))])
    return datax, datay

#Generates vect
"""datax=numpy.array([1,2,3,4,5,6,7,8]) # data coordinates
datay=numpy.array([2.95,6.03,11.2,17.7,26.8, 17.7, 11.2, 6.03])
constraintmaxx=numpy.array([0]) # list of maximum constraints
constraintmaxy=numpy.array([1.2])"""

# least square fit without constraints
# Possible to change model
def fitfunc(x,p): # model $f(x)=a x^2+b x+c
    a,b,c=p
    return c + b*x + a*x**2

def residuals(p): # array of residuals
    return datayTest-fitfunc(dataxTest,p)

def interpolation(n, epsilon):
    p0=[1,0,0] # initial parameters guess
    global dataxTest
    global datayTest
    dataxTest = datax[0:3]
    datayTest = datay[0:3]
    p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
    curve_interpolation = [p]
    curve_points = [0]
    acc=3
    i=4
    while i < n :
        if abs(fitfunc(datax[i],p)) > epsilon:
            dataxTest = datax[(i-2):(i+2)]
            datayTest = datay[(i-2):(i+2)]
            datayTest[0] = fitfunc(datax[i-2],p)
            p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
            pwith=scimin.fmin_slsqp(sum_residuals_custom,p)
            curve_interpolation.append(pwith)
            curve_points.append(i-2)
            acc=3
            i+=1
        else:
            if acc%5 == 0:
                datayTest = datay[curve_points[-1]:i]
                dataxTest = datax[curve_points[-1]:i]
                p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
                curve_interpolation[-1]=p
        acc+=1
        i+=1
    curve_points.append(n-1)
    return curve_interpolation, curve_points


def sum_residuals_custom(p): # the function we want to minimize
    return sum(residuals(p)**2)

datax, datay = generate(50) # comment this if you use vect
curve_interpolation, curve_points = interpolation(len(datax),1)

# plotting

ax=mpl.figure().add_subplot(1,1,1)
ax.plot(datax,datay,ls="",marker="x",color="blue",mew=2.0,label="Datas")
# plotting different regression
for e in range(len(curve_points)-1):
    a = min(datax[curve_points[e]:curve_points[e+1]+1])
    b = max(datax[curve_points[e]:curve_points[e+1]+1])
    morex=numpy.linspace(min(datax[curve_points[e]:curve_points[e+1]+1]),max(datax[curve_points[e]:curve_points[e+1]+1]), endpoint = True)
    ax.plot(morex,fitfunc(morex,curve_interpolation[e]),color="red")
    
ax.legend(loc=2)

mpl.show()