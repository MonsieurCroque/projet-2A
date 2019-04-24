#include "types.h"
#include "TinyGPS++.h"
#include <SoftwareSerial.h>
#include "QmuTactile.h"
#define ESP_SPI_FLASH_H
#include <Wire.h>
#include "SSD1306.h"
#include "stdint.h"
#include "stdbool.h"
#include "stddef.h"
#include "esp_err.h"
#include "sdkconfig.h"

#include "BluetoothSerial.h"
 
BluetoothSerial SerialBT;

#define ESP_ERR_FLASH_BASE       0x10010
#define ESP_ERR_FLASH_OP_FAIL    (ESP_ERR_FLASH_BASE + 1)
#define ESP_ERR_FLASH_OP_TIMEOUT (ESP_ERR_FLASH_BASE + 2)

#define SPI_FLASH_SEC_SIZE  4096    /**< SPI Flash sector size */

#define SPI_FLASH_MMU_PAGE_SIZE 0x10000 /**< Flash cache MMU mapping page size */


#define PIN_BUTTON 0
#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */

QmuTactile button0(PIN_BUTTON);

//Define RX and TX Pin for GPS and Baud Rate for GPS connection
static const int RXPin = 16, TXPin = 17;
static const uint32_t GPSBaud = 9600;

//Creation of an GPS object
TinyGPSPlus gps;

//Creation of a SoftwareSerial for GPS connection
SoftwareSerial ss(RXPin, TXPin);

//Save reading number on RTC memory (keep trak of Reading ID even in Deep Sleep)
RTC_DATA_ATTR int readingID = 0;

void setup() {

  Serial.begin(9600);
  ss.begin(GPSBaud);
  button0.start();
  long memory_const;
  memory_const = 0;
  spi_flash_init();
    
}

template <class T> int Flash_writeAnything(int ee, const T& value)
{
   const byte* p = (const void*)&value;
   int i;
   spi_flash_write(ee, *p, 2);
}

template <class T> int Flash_readAnything(int ee, T& value)
{
   byte* p = (byte*)(void*)&value;
   int i;
   spi_flash_read(ee, *p, 2);
}
 
void callback(esp_spp_cb_event_t event, esp_spp_cb_param_t *param){
  if(event == ESP_SPP_SRV_OPEN_EVT){
    Serial.println("Client Connected");
  }
}

void loop() {

    // Sleep 
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
    
    // Store and print new point
    long writeValue;
    writeValue = gps.location.lat() * 1000000;
    Serial.print("LAT=");  Serial.println(writeValue, 6);
    Flash_writeAnything(memory_const, writeValue);
    memory_const = memory_const + 2;
    writeValue = gps.location.lng() * 1000000;
    Serial.print("LONG=");  Serial.println(writeValue, 6);
    Flash_writeAnything(memory_const, writeValue);
    memory_const = memory_const + 2;
    writeValue = gps.altitude.meters * 1000000;
    Serial.print("ALT=");  Serial.println(writeValue, 6);
    Flash_writeAnything(memory_const, writeValue);
    memory_const = memory_const + 2;
  }


    // if button pressed then print all memory
    if (button0.getState() == TACTILE_STATE_LONG_PRESS) {

         SerialBT.register_callback(callback);
   
         if(!SerialBT.begin("ESP32")){
           Serial.println("An error occurred initializing Bluetooth");
         }else{
           Serial.println("Bluetooth initialized");
         }
         int i;
         i = 0;       
         while (i < memory_const){
             long readValue;
             Flash_readAnything(i, readValue);
             SerialBT.print("LAT=");  SerialBT.print(readValue, 6);
             i = i + 2;
             Flash_readAnything(i, readValue);
             SerialBT.print("LONG=");  SerialBT.print(readValue, 6);
             i = i + 2;
             Flash_readAnything(i, readValue);
             SerialBT.print("ALT=");  SerialBT.print(readValue, 6);
             i = i + 2;
         }
    }
}
