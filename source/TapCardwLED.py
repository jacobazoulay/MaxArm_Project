import time
import sys
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from espmax import ESPMax
from RobotControl import RobotControl
from TM1640 import TM1640
from Color_sensor import COLOR
from machine import Pin, I2C
from micropython import const

nozzle = SuctionNozzle()
bus_servo = BusServo() 
arm = ESPMax(bus_servo)

i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
apds = COLOR(i2c)
apds.enableLightSensor(True)

tm = TM1640(clk=Pin(33), dio=Pin(32))

tm.tube_display("8888")
print("Card Tapping Test")

def TapCard(NumOfTap = 0):
  
  nozzle.on()
  tm.tube_display("    ")   # Clears the LED Counter 
  for i in range(NumOfTap):
  #moves card to the lock
    bus_servo.run(1, 135, 250)
    time.sleep_ms(250)
  
    bus_servo.run(2, 359, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 630, 250)
    tm.tube_display(i+1)
    time.sleep_ms(1000)  #2500
  
  #moves card above the lock
    bus_servo.run(1, 135, 250)
    time.sleep_ms(250)
  
    bus_servo.run(2, 415, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 468, 250)
    #tm.tube_display(2)
    time.sleep_ms(1000) #3000
  nozzle.off()
  
