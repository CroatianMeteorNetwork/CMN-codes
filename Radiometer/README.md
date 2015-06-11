Radiometer
==========

The goal of this project is to make a low-cost radiometer for fireball observations.
The current goal is to have 12-bit data from a photodiode sampled at about 3kHz which would show high-frequency characteristics in the fireball's lightcurve.

*Current status:*
Sampling the potentiometer at about 3150 Hz with 11-bits of data (0 to 5V, for full range of 12-bits -5 to +5V is needed). The data is recorded via a Python script, and the 10 seconds of recorded data is shown as a graph. The solenoid is activated during the recording peroid via the relay shield.

This project uses several different libraries:
- modified Adafruit_ADS1X15 library for working with 12-bit Adafruit ADC ADS1015
- pySerial for serial communication with Arduino and Python

Parts used:
- Arduino Uno R3
- Adafruit ADS1015 breakout board
- ZYE1-0837ZP solenoid (cues during the day to protect the photodiode from the Sun)
- Arduino relay shield for switching on the solenoid
- photodiode and OP - still waiting for their arrival

Work to be done:
- test the photodiode and the OP with current setup
- test a few wide-angle lenses and design a solution how to focus the light into the dioide
- design a small metal arm which would be deployed during the day to protect the photodiode from the Sun
- finish the prototype and design a PCB -> solder the components
- pack everything into a nifty little box
- write software to make 1 minute files with recorded data
- write viewer software to view the data
- write software for fireball detection