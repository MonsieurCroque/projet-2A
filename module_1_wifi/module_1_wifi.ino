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
float writeValue; //current gps coordinate

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

      //new point in memory
      writeValue = gps.location.lat();     
      EEPROM.write(memory_addr, writeValue);
      memory_addr = memory_addr + 1;
      writeValue = gps.location.lng();
      EEPROM.write(memory_addr, writeValue);
      memory_addr = memory_addr + 1;
      EEPROM.commit();
      
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
             float readValue;
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
