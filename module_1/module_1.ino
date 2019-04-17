#include "types.h"
#include "TinyGPS++.h"
#include "HardwareSerial.h"
#include "QmuTactile.h"
#define ESP_SPI_FLASH_H
#include <Wire.h>
#include "SSD1306.h"
#include "stdint.h"
#include "stdbool.h"
#include "stddef.h"
#include "esp_err.h"
#include "sdkconfig.h"

#define ESP_ERR_FLASH_BASE       0x10010
#define ESP_ERR_FLASH_OP_FAIL    (ESP_ERR_FLASH_BASE + 1)
#define ESP_ERR_FLASH_OP_TIMEOUT (ESP_ERR_FLASH_BASE + 2)

#define SPI_FLASH_SEC_SIZE  4096    /**< SPI Flash sector size */

#define SPI_FLASH_MMU_PAGE_SIZE 0x10000 /**< Flash cache MMU mapping page size */


#define PIN_BUTTON 0
#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */

QmuTactile button0(PIN_BUTTON);

TinyGPSPlus gps;
HardwareSerial SerialGPS(1);

GpsDataState_t gpsState = {};

#define TASK_OLED_RATE 200
#define TASK_SERIAL_RATE 100

uint32_t nextSerialTaskTs = 0;
uint32_t nextOledTaskTs = 0;

void setup() {

    Serial.begin(115200);
    SerialGPS.begin(9600, SERIAL_8N1, 16, 17);
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

void loop() {

    static int p0 = 0;

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

    // if button pressed then print all memory
    if (button0.getState() == TACTILE_STATE_LONG_PRESS) {
         int i;
         i = 0;       
         while (i < memory_const){
             long readValue;
             Flash_readAnything(i, readValue);
             Serial.print("LAT=");  Serial.print(readValue, 6);
             i = i + 2;
             Flash_readAnything(i, readValue);
             Serial.print("LONG=");  Serial.print(readValue, 6);
             i = i + 2;
             Flash_readAnything(i, readValue);
             Serial.print("ALT=");  Serial.print(readValue, 6);
             i = i + 2;
         }
    }
}
