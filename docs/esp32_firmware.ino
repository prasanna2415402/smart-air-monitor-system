/*
 * Smart IAQ Monitoring System - ESP32 Firmware
 * ----------------------------------------------
 * Reads CO2 (MH-Z19B), Temperature/Humidity (DHT22), PM2.5/PM10 (PMS5003),
 * and Barometric Pressure (BMP280). Sends one JSON line per cycle over USB
 * Serial at 115200 baud, matching what data_source.py expects. Shows status
 * on an SSD1306 OLED, sounds a buzzer on threshold breach, and accepts
 * FAN_ON / FAN_OFF commands from the Python backend to drive a relay.
 *
 * Libraries required (Arduino Library Manager):
 *   DHT sensor library (Adafruit), Adafruit BMP280, Adafruit SSD1306,
 *   Adafruit GFX, MHZ19 (by strange-v), ArduinoJson, PMS (by fu-hsi)
 */

#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MHZ19.h>
#include <HardwareSerial.h>
#include <ArduinoJson.h>
#include <PMS.h>

// ---------------- Pin Definitions ----------------
#define DHT_PIN      4
#define RELAY_PIN    32
#define BUZZER_PIN   33
#define DHT_TYPE     DHT22

// ---------------- Sensor Objects ----------------
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_BMP280 bmp;
Adafruit_SSD1306 display(128, 64, &Wire, -1);
MHZ19 mhz;
HardwareSerial mhzSerial(2);   // UART2: MH-Z19B  (RX=16, TX=17)
HardwareSerial pmsSerial(1);   // UART1: PMS5003  (RX=25, TX=26)
PMS pms(pmsSerial);
PMS::DATA pmsData;

// ---------------- Thresholds (mirrors alerts.py defaults) ----------------
const float CO2_WARN   = 1000.0;
const float PM25_WARN  = 25.0;

unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL_MS = 5000;

void setup() {
  Serial.begin(115200);                       // USB serial to PC
  mhzSerial.begin(9600, SERIAL_8N1, 16, 17);   // MH-Z19B
  pmsSerial.begin(9600, SERIAL_8N1, 25, 26);   // PMS5003

  dht.begin();
  bmp.begin(0x76);
  mhz.begin(mhzSerial);
  mhz.autoCalibration(true);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("{\"error\":\"OLED init failed\"}");
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Warm-up notice (MH-Z19B needs ~3 minutes for stable readings)
  display.setCursor(0, 0);
  display.println("IAQ Monitor");
  display.println("Warming up sensors...");
  display.display();
}

void handleIncomingCommands() {
  // Python backend sends "FAN_ON\n" / "FAN_OFF\n" to drive the relay
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "FAN_ON") {
      digitalWrite(RELAY_PIN, HIGH);
    } else if (cmd == "FAN_OFF") {
      digitalWrite(RELAY_PIN, LOW);
    }
  }
}

void updateDisplay(float co2, float temp, float hum, float pm25, bool alert) {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  display.printf("CO2: %.0f ppm\n", co2);
  display.printf("Temp: %.1fC  Hum: %.0f%%\n", temp, hum);
  display.printf("PM2.5: %.1f ug/m3\n", pm25);
  display.printf("Fan: %s\n", digitalRead(RELAY_PIN) ? "ON" : "OFF");
  if (alert) {
    display.println("*** ALERT ***");
  }
  display.display();
}

void loop() {
  handleIncomingCommands();

  if (millis() - lastReadTime < READ_INTERVAL_MS) {
    return;
  }
  lastReadTime = millis();

  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  int   co2  = mhz.getCO2();
  float pressure = bmp.readPressure() / 100.0F; // Pa -> hPa

  float pm25 = 0, pm10 = 0;
  if (pms.readUntil(pmsData, 1000)) {
    pm25 = pmsData.PM_AE_UG_2_5;
    pm10 = pmsData.PM_AE_UG_10_0;
  }

  // Guard against NaN from a failed DHT read so JSON stays valid
  if (isnan(temp)) temp = 0;
  if (isnan(hum))  hum  = 0;

  bool alert = (co2 > CO2_WARN) || (pm25 > PM25_WARN);

  StaticJsonDocument<256> doc;
  doc["co2_ppm"]     = co2;
  doc["temperature"] = temp;
  doc["humidity"]    = hum;
  doc["pm25"]        = pm25;
  doc["pm10"]        = pm10;
  doc["pressure"]    = pressure;

  serializeJson(doc, Serial);
  Serial.println();

  updateDisplay(co2, temp, hum, pm25, alert);

  if (alert) {
    tone(BUZZER_PIN, 2000, 400);
  }
}
