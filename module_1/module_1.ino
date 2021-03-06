#include "types.h"
#include "TinyGPS++.h"
#include <SoftwareSerial.h>
#include <Wire.h>
#include "EEPROM.h"

#define EEPROM_SIZE 550 // number of bytes you want to access (up to 4Mb cf doc)

const int buttonPin = 4;    // the number of the pushbutton pin
int buttonState;             // the current reading from the input pin

//Define RX and TX Pin for GPS and Baud Rate for GPS connection
static const int RXPin = 16, TXPin = 17;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps; //creation of an GPS object

SoftwareSerial ss(RXPin, TXPin); //creation of a SoftwareSerial for GPS connection

long memory_addr; //current memory pointer

//Save reading number on RTC memory (keep trak of Reading ID even in Deep Sleep)
//RTC_DATA_ATTR int readingID = 0;

void setup() {

  Serial.begin(9600);

  //set GPS
  ss.begin(GPSBaud);
  
  //set flash memory
  memory_addr = 0;
  EEPROM.begin(EEPROM_SIZE);
  
  //set button
  pinMode(buttonPin, INPUT);

}


void loop() {

  while(ss.available() > 0){
    
    if (gps.location.isUpdated()){

      long writeValue = gps.location.lat();
      Serial.println(writeValue, 6);
      EEPROM.write(memory_addr, writeValue);
      EEPROM.commit();
      memory_addr = memory_addr + 2;
      long writeValue = gps.location.lng();
      Serial.println(writeValue, 6);
      EEPROM.write(memory_addr, writeValue);
      EEPROM.commit();
      
    }
  }
  
  buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH) {

    int i = 0;
    while (i < memory_addr){
       long readValue;
       readValue = EEPROM.read(i);
       Serial.println(readValue);
       i = i + 1;
    }

  }
  Serial.println("over");
    
}
