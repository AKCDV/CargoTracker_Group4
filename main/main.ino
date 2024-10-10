#include "DHT.h"

// Define the pin connected to the DHT11 data pin
#define DHTPIN 7  // DHT11 is connected to digital pin 7

// Define DHT type
#define DHTTYPE DHT11  // DHT11 sensor

// Create a DHT object
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Start the serial communication to monitor values
  Serial.begin(9600);
  Serial.println("DHT11 Humidity and Temperature Sensor Test");

  // Initialize the DHT sensor
  dht.begin();
}

void loop() {
  delay(2000);

  // Read humidity
  float humidity = dht.readHumidity();

  // Read temperature as Celsius 
  float temperature = dht.readTemperature();

  // Check if any reads failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Print the results to the Serial Monitor
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  // logic to alert if humidity crosses a threshold
  if (humidity > 70) {  // Example threshold
    Serial.println("Warning: Humidity is too high!");
  }
}
