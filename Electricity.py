#!/usr/bin/python3
########################
# Energy Meter Data Logging - Electric
# Adam Hedley
# August 2019
#
# Use meter pulse to monitor energy usage and store
# data to MySQL database
#     ___          ___
#  __|   |________|   |___
#
# Count every falling edge for daily energy usage
# Electric Meter
# 1 pulse = 1 Wh
# 1000 pulses = 1 kWh
# Reset pulse counts at midnight
#
# Measures time between falling and rising edge and adds
# pulse width to calculate current power. Pulse width dependent
# on meter type.
#
# LDR needs to be stuck onto meter flashing LED with no external 
# light leaking. Double sided sticky pads seem to work fine.  
# 
# LDR Circuit
#
# 3V3 ___________
#         |
#         -
#        | |  LDR (170 Ohm - 1.3 M Ohm - RS466-1996)
#         -
#         |
# DIO ____|
#         |
#         -
#        | |  10K Ohm
#         -
#         | 
# GND ————————————
#
# For setting up MySQL and setting up web server to display 
# data via web browser follow 
# https://projects.raspberrypi.org/en/projects/lamp-web-server-with-wordpress
#
# MySQL
# Database: Meters
# Tables  : Electric
#         : Car
#         : GAS
########################

import serial
import time
import datetime
import RPi.GPIO as GPIO
import mysql.connector
from mysql.connector import errorcode

# Set initial values to zero
energy = 0
power = 0
start_time = time.time() # to account for first read being a rising edge
end_time = 0
state = 0


print(" ")
print("Setting up DIO pins...")
print(" ")

# DIO pin used to read meter pulse
meter_pin = 7

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)      # GPIO pin numbering mode
GPIO.setwarnings(False)       # Ignore warnings
# Set GPIO pin as input, add pull-down and event detection
GPIO.setup(meter_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(meter_pin, GPIO.BOTH) # Add event detection for both rising and falling edge

print ("DIO Set Up")
print (" ")

# Save Data to MySQL database
def database(energy, power, datetime, timestamp):
  try:
    # Open a connection to the MySQL Server - change user, password and database accordingly 
    cnx = mysql.connector.connect(user='root', password='raspberry', database='Meter')
    # Create a new Cursor
    cursor = cnx.cursor()
    # Insert a new row into the table
    add_data = ("INSERT INTO Electric "
               "(energy, power, datetime, date) "
               "VALUES (%s, %s, %s, %s)")

    # Setting the data values
    data_val = (energy, power, datetime, timestamp)
    #print ("data_val: ",data_val)
    #print (" ")
    # Passing all the data to the cursor
    cursor.execute(add_data, data_val)
    # Make sure the data is committed to the database
    cnx.commit()
    # Close the cursor
    cursor.close()
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist numnuts”)
    else:
      print(err)
  else:
    cnx.close()

  #print ("MySQL connection is closed")
  #print (" ")


def main():

  print ("Main part...")
  print (" ")

  start_time = time.time()
  energy = 0
  state = 0
  # Meter output pulse width
  pulse_width = 0.170  # 170 ms. Assumed it was 50 ms but seems to be 170

  while True:

    # Reset Energy usage to zero at start of day
    midnight = datetime.datetime.now()
    midnight = midnight.strftime("%H:%M:%S")
    #print ("Midnight time : ",midnight)
    #print (" ")
    if midnight == "00:00:00":
      energy = 0

    # Wait for falling edge
    GPIO.wait_for_edge(meter_pin, GPIO.FALLING)
    start_time = time.time()
    energy +=1
    # Add sleep in case of signal debouncing, thus negate false readings - not actually needed now
    time.sleep(0.2) # 250 ms = max power of ~14.4 kW - won’t use that much.. I hope

    # Checking DIO state 
    state = GPIO.input(meter_pin)
    print ("Low State :     ", state)
    print (" ")

    print ("Energy Usage :  ",energy)
    print (" ")

    # Rising edge detection
    GPIO.wait_for_edge(meter_pin, GPIO.RISING)
    state = GPIO.input(meter_pin)
    print ("High State :    ", state)
    print (" ")

    end_time = time.time()
    #print ("End time: ", end_time, " Start time: ", start_time, " PW: ", pulse_width)
    #print (" ")

    elapsed_time = (end_time - start_time) + pulse_width
    print ("Elapsed time :  ",elapsed_time)
    print (" ")

    power = 3600 / elapsed_time
    pwr = "%.2f" %power
    print ("Current Power : ",pwr, " WATTS")
    print (" ")

    # Send data to the database
    now = datetime.datetime.now()
    timestamp = now.strftime("%d.%m.%Y %H:%M")
    secs = int(time.time())  # Unix time stamp for HighCharts
    database(energy, power, timestamp, secs)


if __name__=="__main__":
 		main()
