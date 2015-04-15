#include <Wire.h>
#include <Adafruit_ADS1015.h>

Adafruit_ADS1015 ads; /* Use thi for the 12-bit version */


// Define constants
const int analogPin = 0;
const int irisRelayOut = 12;

// Define variables
int irisCommand;
int enableTimer = 0;
int ADCValue;

int16_t result;

byte b1, b2;


void irisOff(){
  // Used for closing the iris
  digitalWrite(irisRelayOut, LOW);
  enableTimer = 0;
  delay(10);
  Serial.println("Response");
  
  }
  
void irisOn(){
  // Used for opening the iris
  digitalWrite(irisRelayOut, HIGH);
  Serial.println("Response");
  // Allow some to for Iris to open before starting to record
  delay(200);
  enableTimer = 1;
  }
  
void setupTimer2(){
  
  // TIMER SETUP- the timer interrupt allows preceise timed measurements
  //for mor info about configuration of arduino timers see http://arduino.cc/playground/Code/Timer1
  cli();//stop interrupts

  //set timer0 interrupt at 3125 Hz
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 2khz increments
  //OCR2A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256) 1kHz
  //OCR2A = 99;// = (16*10^6) / (2500*64) - 1 (must be <256) 2k5Hz
  OCR2A = 94;// = (16*10^6) / (2500*64) - 1 (must be <256) 2k5Hz (tweaked)
  // turn on CTC mode
  TCCR2A |= (1 << WGM01);
  
  // Set CS21 and CS20 bits for 64 prescaler
  TCCR2B |= (1 << CS22) | (0 << CS21) | (0 << CS20);  
  
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
  
  sei();//allow interrupts
  //END TIMER SETUP
  
  }
  
void setupTimer1(){
  
  // TIMER SETUP- the timer interrupt allows preceise timed measurements
  //for mor info about configuration of arduino timers see http://arduino.cc/playground/Code/Timer1
  cli();//stop interrupts

  //set timer1 interrupt at 3125 Hz
  TCCR1A = 0;// set entire TCCR2A register to 0
  TCCR1B = 0;// same for TCCR2B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 2khz increments
  //OCR1A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256) 1kHz
  //OCR1A = 99;// = (16*10^6) / (2500*64) - 1 (must be <256) 2k5Hz
  OCR1A = 20;// = (16*10^6) / (3125*256) - 1 (must be <256) 3125 Hz
  //OCR1A = 124;// = (16*10^6) / (3125*256) - 1 (must be <256) 500 Hz
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  
  // Set CS11 and CS10 bits for 64 prescaler
  //TCCR1B |= (1 << CS11) | (1 << CS10);  
  
  // Set CS10 and CS11, CS12 bits for 256 prescaler
  TCCR1B |= (1 << CS12) | (0 << CS11)| (0 << CS10);
  
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);
  
  sei();//allow interrupts
  //END TIMER SETUP
  
  }
  
void setupTimer0(){
  
  // TIMER SETUP- the timer interrupt allows preceise timed measurements
  //for mor info about configuration of arduino timers see http://arduino.cc/playground/Code/Timer1
  cli();//stop interrupts

  //set timer0 interrupt at 3125 Hz
  TCCR0A = 0;// set entire TCCR2A register to 0
  TCCR0B = 0;// same for TCCR2B
  TCNT0  = 0;//initialize counter value to 0
  // set compare match register for 2khz increments
  //OCR0A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256) 1kHz
  //OCR0A = 99;// = (16*10^6) / (2500*64) - 1 (must be <256) 2k5Hz
  OCR0A = 20;// = (16*10^6) / (3125*256) - 1 (must be <256) 3125 Hz
  //OCR0A = 124;// = (16*10^6) / (3125*256) - 1 (must be <256) 500 Hz
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  
  // Set CS11 and CS10 bits for 64 prescaler
  //TCCR0B |= (1 << CS01) | (1 << CS00);  
  
  // Set CS10 and CS11, CS12 bits for 256 prescaler
  TCCR0B |= (1 << CS02) | (0 << CS01)| (0 << CS00);
  
  // enable timer compare interrupt
  TIMSK0 |= (1 << OCIE0A);
  
  sei();//allow interrupts
  //END TIMER SETUP
  
  }
  

void setup(){
  pinMode(irisRelayOut, OUTPUT);
  
  // Timer2 must be used bas Timer0 creates conflicts with the Serial library and Timer1 data is not very reliable (I concluded that from experiments, don't know why that happens)
  setupTimer2();
  
  Serial.begin(115200);
  ads.begin();
  
  //Set I2C speed to max
  TWBR = 1;
  
}

ISR(TIMER2_COMPA_vect){//Interrupt at freq of 3125 Hz to measure analog value
  sei();
  
  if (enableTimer == 0) return;
  
/*
  // Arduino internal ADC
  // Read analog value
  ADCValue = analogRead(analogPin);

  // Convert data to 2 bytes for sending
  b1 = ADCValue&0xFF;
  b2 = ( ADCValue >> 8 ) & 0xFF;
  
  // Send data
  Serial.write(b1);
  Serial.write(b2);
  */
  
  
  //Adafruit ADC
  // Read analog value
  
  // SLOWING THINGS DOWN:
  result = ads.readADC_Differential_0_1();
  result += 2048;
  
  ADCValue = (int) result;
  
  // Convert data to 2 bytes for sending
  b1 = ADCValue&0xFF;
  b2 = ( ADCValue >> 8 )& 0xFF;
  
  // Send data
  Serial.write(b1);
  Serial.write(b2);
  
  
}

void loop(){
  
  // Monitor incoming signals for iris closing and opening
  while (Serial.available() > 0) {
  
      // look for the next valid integer in the incoming serial stream:
      irisCommand = Serial.parseInt();
      
      if (irisCommand == 1) irisOn();
      else irisOff();
      
      }
      
}



