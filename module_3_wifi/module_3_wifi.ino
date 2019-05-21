#include "types.h"
#include "TinyGPS++.h"
#include <SoftwareSerial.h>
#include <Wire.h>
#include "EEPROM.h"
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>

// Set these to your desired credentials.
const char *ssid = "ESP32";
const char *password = "yourPassword";

WiFiServer server(80); // set wifi server

#define EEPROM_SIZE 550 // number of bytes you want to access (up to 4Mb cf doc)

const int buttonPin = 4;    // the number of the pushbutton pin
int buttonState;             // the current reading from the input pin

//Define RX and TX Pin for GPS and Baud Rate for GPS connection
static const int RXPin = 16, TXPin = 17;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps; //creation of an GPS object

SoftwareSerial ss(RXPin, TXPin); //creation of a SoftwareSerial for GPS connection..............

float memory_addr; //current memory pointer
float longitude; //current gps longitude
float latitude; //current gps latitude

float coord0[2] = {-1000,-1000};  // point for slope
float coord1[2] = {-1000,-1000};  // point for slope
float coord2[2] = {-1000,-1000};  // new point
float coordM[2]; // point before changing

const float espi = 10/6300000; // precision to achieve in meters
const float pi = 3.14;

// copy content array in target array with length of 2
void copy(float target[], float content[]){
  target[0] = content[0];
  target[1] = content[1];
}

//Distance between point and slope in cartesian
float distance(float coord0[],float coord1[], float coord2[]){
    return ((coord1[1]-coord0[1])*coord2[0]-(coord1[0]-coord0[0])*coord2[1] + coord1[0]*coord0[0] - coord1[1]*coord0[0])/sqrt(pow(coord1[1]-coord0[1], 2) + pow(coord1[0]-coord0[0],2));
}


void setup() {

  Serial.begin(9600);

  //set GPS
  ss.begin(GPSBaud);
  
  //set flash memory
  memory_addr = 0;
  EEPROM.begin(EEPROM_SIZE);
  
  //set button
  pinMode(buttonPin, INPUT);

  //set wifi server
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  server.begin();

}


void loop() {

  while(ss.available() > 0){
    gps.encode(ss.read());
    
    if (gps.location.isUpdated()){

      latitude = gps.location.lat();
      longitude = gps.location.lng();

      //initialization
      if (coord0[0] == -1000){

        coord0[0] = longitude;
        coord0[1] = latitude;
        
        //starting point in memory
        EEPROM.write(memory_addr, longitude);
        memory_addr = memory_addr + 1;
        EEPROM.write(memory_addr, latitude);
        memory_addr = memory_addr + 1;
        EEPROM.commit();
      
      }
      else if (coord1[0] == -1000){

        coord1[0] = longitude;
        coord1[1] = latitude;
      }

      else{ //after initialization

        coord2[0] = latitude;
        coord2[1] = longitude;
        
        if (distance(coord0,coord1,coord2) > epsi){

          Serial.println("newPoint");
          Serial.println(longitude, latitude);

          //last valid point in memory
          EEPROM.write(memory_addr, coordM[0]);
          memory_addr = memory_addr + 1;
          EEPROM.write(memory_addr, coordM[1]);
          memory_addr = memory_addr + 1;
          EEPROM.commit();

          //new starting point in memory
          EEPROM.write(memory_addr, longitude);
          memory_addr = memory_addr + 1;
          EEPROM.write(memory_addr, latitude);
          memory_addr = memory_addr + 1;
          EEPROM.commit();

          //change slope
          copy(coord0, coordM);
          copy(coord1, coord1);
        }
      
      else{ // if current slope good enough

        // take last point
        coordM[0] = longitude;
        coordM[1] = latitude;
      }
    }
  }
  }
  
  buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH) {

      WiFiClient client = server.available();   // listen for incoming clients
      
      while (client) {                             // if you get a client,
          
          while (! client.connected()) {
            Serial.println("wait");// wait for client
          }
          
          int i = 0;
          while (i < memory_addr){
             long readValue;
             readValue = EEPROM.read(i);
             Serial.println(readValue);
             client.write(readValue);  //send value to client
             i = i + 1;
          }
          break;
        }
  client.stop(); // close the connection
  Serial.println("over");
  }
}
