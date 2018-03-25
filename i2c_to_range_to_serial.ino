#include <Wire.h>

#define SLAVE_ADDRESS 0x04
int number = 0;
int state = 0;

const int pingPin = 7;
const int discoPin = 5;
unsigned int duration, inches;
int delaylength = 3000;


void setup() {
  Serial.begin(9600);
  pinMode(5, OUTPUT);

  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);  

  }


void loop(){
}

void git_data(void)
{
  // establish variables for duration of the ping, 
  // and the distance result in inches and centimeters:
  long duration, inches, cm;

  // The PING))) is triggered by a HIGH pulse of 2 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
  pinMode(pingPin, OUTPUT);
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pingPin, LOW);

  // The same pin is used to read the signal from the PING))): a HIGH
  // pulse whose duration is the time (in microseconds) from the sending
  // of the ping to the reception of its echo off of an object.
  pinMode(pingPin, INPUT);
  duration = pulseIn(pingPin, HIGH);

  // convert the time into a distance
  inches = microsecondsToInches(duration);
  cm = microsecondsToCentimeters(duration);
  //  inches = duration / 74 / 2;        // Convert to inches

  Serial.print("inches=");
  Serial.print(inches);
  Serial.print(" cm=");
  Serial.print(cm);
  Serial.println();

  if (inches < 6) {
    digitalWrite(discoPin, HIGH);   
  }

  else {
    digitalWrite(discoPin,LOW);
  }

  delay(500);
}


// callback for sending data
void sendData(){
  Wire.write(number);
}

// callback for received data
void receiveData(int byteCount){

  while(Wire.available()) {
    number = Wire.read();

    if (number == 1){
      git_data();
    }
  }
}

long microsecondsToInches(long microseconds)
{
  // According to Parallax's datasheet for the PING))), there are
  // 73.746 microseconds per inch (i.e. sound travels at 1130 feet per
  // second).  This gives the distance travelled by the ping, outbound
  // and return, so we divide by 2 to get the distance of the obstacle.
  // See: http://www.parallax.com/dl/docs/prod/acc/28015-PING-v1.3.pdf
  return microseconds / 74 / 2;
}

long microsecondsToCentimeters(long microseconds)
{
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the
  // object we take half of the distance travelled.
  return microseconds / 29 / 2;
}







