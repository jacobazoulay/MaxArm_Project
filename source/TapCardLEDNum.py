import time
import sys
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from Arm import Arm
from Robot import Robot
from TM1640 import TM1640
from ColorSensor import ColorSensor
from machine import Pin, I2C
from micropython import const

nozzle = SuctionNozzle()
bus_servo = BusServo() 
arm = Arm(bus_servo)

i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
apds = ColorSensor(i2c)
apds.enableLightSensor(True)

tm = TM1640(clk=Pin(33), dio=Pin(32))

NumOfTap = 5

if __name__ == '__main__':
  
  #nozzle.on()
  tm.tube_display("    ")   # Clears the LED Counter 
  for i in range(NumOfTap):
#moves card to the lock
    bus_servo.run(1, 135, 250)
    time.sleep_ms(250)
  
    bus_servo.run(2, 359, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 630, 250)
    tm.tube_display(i+1)
    time.sleep_ms(500)  #2500
  
#moves card above the lock
    bus_servo.run(1, 135, 250)
    time.sleep_ms(250)
  
    bus_servo.run(2, 415, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 468, 250)
    #tm.tube_display(2)
    time.sleep_ms(1000) #3000
  nozzle.off()
  

