# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 15:05:23 2019

@author: simon
"""

import bluetooth

#----------------------------data from ESP32-----------------------------------

#Get data from ESP32
file_object  = open("toast0.txt", "w") 
i= 0

while True:
    hostMACAddress = '28:e3:47:07:e5:23' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
    hostMACAddress = '30:ae:a4:8f:f0:de'
    port = 7
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.connect((hostMACAddress, port))
    i = 0
    while i < 10000:
        newData = raw_input()
        i += 0.00001
        if newData != None:
            break
        dataAcc += newData
        print(newData)
        file_object.write(str(newData))
    
    print("received [%s]" % dataAcc)
    
    client_socket.close()
    server_socket.close()
    break

file_object.close()
