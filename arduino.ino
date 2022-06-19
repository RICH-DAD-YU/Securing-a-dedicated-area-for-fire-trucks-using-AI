#include <BH1750FVI.h>
#include <Adafruit_NeoPixel.h>
#define PIN 13   // input pin Neopixel is attached to
#define NUMPIXELS      64 // number of neopixels in strip
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int delayval = 100; // timing delay in milliseconds

//Define for ISD1820
#define PLAY_E 9
#define playTime 5000 // playback time 5 seconds

//Define for light sensor
BH1750FVI LightSensor(BH1750FVI::k_DevModeContLowRes);

void setup() {
  Serial.begin(115200);
  LightSensor.begin();   
  // Initialize the NeoPixel library.
  pixels.begin();
  pixels.Color(0,0,0);
  pinMode(PLAY_E,OUTPUT);
}

void loop() {
  // LED + Light sensor
  uint16_t lux = LightSensor.GetLightIntensity();
  //Serial.print("Light: ");
  //Serial.println(lux);
  if (lux <100) LED(255,255,0); //set led yellow
  else LED(0,0,0); //set led off

  String alert = Serial.readString();
  int cmd = alert.toInt();
  //String check_cmd = "Check cmd: "+ cmd;
  //cmd = 1;
  if (cmd==1){
    digitalWrite(PLAY_E, HIGH);
    delay(50);
    digitalWrite(PLAY_E, LOW);  
    Serial.println("Playbak Started");
    delay(playTime);
    Serial.println("Playbak Ended");                         
  }
  delay(delayval);
}

void LED(int r, int g, int b){
  for (int i=0; i < NUMPIXELS; i++) {
      pixels.setPixelColor(i, pixels.Color(r,g,b));
      pixels.setBrightness(128);
      pixels.show();    
  }
}
