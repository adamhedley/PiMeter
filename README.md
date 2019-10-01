# PiMeter
Home Energy Metering using a Raspberry Pi 


Simple way to use a raspberry pi to monitor electric and or gas meters using the flashing led indicator. 
This will be updated when after significant changes (when I remember to). But for now it's a starting point. I am new to software so there are probably much better ways to do this. But for me it works.  

Use meter pulse to monitor energy usage and store
data to MySQL database
     ___          ___
  __|   |________|   |___

Count every falling edge for daily energy usage
Electric Meter
1 pulse = 1 Wh
1000 pulses = 1 kWh
Reset pulse counts at midnight

Measures time between falling and rising edge and adds pulse width to calculate current power. Pulse width dependent
on meter type.

LDR needs to be stuck onto meter flashing LED with no external light leaking. Double sided sticky pads seem to work fine at making a tight seal.  
 
LDR Circuit

 3V3 ___________
         | 
         -
        | |  LDR (170 Ohm - 1.3 M Ohm - RS466-1996)
         -
         |
 DIO ____|
         |
         -
        | |  10K Ohm
         -
         | 
GND ————————————

For setting up MySQL and setting up web server to display data via web browser follow 
https://projects.raspberrypi.org/en/projects/lamp-web-server-with-wordpress
