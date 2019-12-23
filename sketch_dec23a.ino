#include <stdint.h>
#include <avr/io.h>
#include <util/twi.h>
#include <util/delay.h>
#include <avr/pgmspace.h>
#include <Wire.h>
#include <dht11.h>

dht11 DHT11;

#define DHT11PIN 36
#define CAMERA_ADDRESS 0x21

int data_p[] = {22, 23, 24, 25, 26, 27, 28, 29};
int xclock_p = 10;
int pclock_p = 2;
int href_p = 8;
int vsynch_p = 3;

int x;
int y;

float humidity;
float temperature;

void setup() {
  delay(5000);
  Serial.begin(1000000);
  for (int i = 0; i < 8; i++) {
    pinMode(data_p[i], INPUT);
  }
  // configure rest input pins
  pinMode(xclock_p, OUTPUT);
  pinMode(pclock_p, INPUT);
  pinMode(href_p, INPUT);
  pinMode(vsynch_p, INPUT);
  pinMode(38, OUTPUT); // humadity
  pinMode(40, OUTPUT); // temp
  Wire.begin();

  cli();
  ASSR &= ~(_BV(EXCLK) | _BV(AS2));
  TCCR2A = (1 << COM2A0) | (1 << WGM21) | (1 << WGM20);
  TCCR2B = (1 << WGM22) | (1 << CS20);
  OCR2A = 0;//(F_CPU)/(2*(X+1))
  sei();
  writeCameraRegister(0x12, 0x80); // reset all camera registers to default value
  delay(1000); // wait for reset proccess to be done (because it is quite slow)
}

void loop() {
//  byte d=0;
//  for (int i=0; i<8; i++){
//    d |= digitalRead(data_p[i]) << data_p[i];
//  }
  int chk = DHT11.read(DHT11PIN);
  humidity = (float)DHT11.humidity;
  if (humidity>50.0) {
    digitalWrite(38,HIGH);
  }
  else{
    digitalWrite(38,LOW);
  }
  temperature = (float)DHT11.temperature;
  if (temperature>25.0){
    digitalWrite(40,HIGH);
  }
  else{
    digitalWrite(40,LOW);
  }


  cli();
  while(!(PINE & 32)); // vsync wait high
  while((PINE &32));  // vsync wait low
  y = 480;
  while (y--){
    x = 1280;
    while(x--){
      while(!(PINH & 32)); // wait hre high
      while(!(PINE & 16)); //wait for high
      while((PINE & 16)); // wait for low
      while(!(UCSR0A & (1 << UDRE0)));
      UDR0 = PINA;
      while(!(PINE & 16)); //wait for high
      while((PINE & 16)); // wait for low
    }
  }
  sei();
}

void writeCameraRegister(byte registerId, byte registerValue) {
  Wire.beginTransmission(CAMERA_ADDRESS);
  Wire.write(registerId);
  Wire.write(registerValue);
  Wire.endTransmission();
  delay(1);
}
