########################################################################################################
# Systems Automation - Getting READ Range of Credential to any LOCK
# Copyright (R) ASSA ABLOY   -  Joel Albarracin , 26 March 2024
#                               Jacob Azoulay
#
# Python script using MaxArm Robotic Arm on getting READ Range for Credential
#  On Terminal: TapCard (a, b, c, d)
#                  where a: number of presentations/tap
#                        b: distance in mm (units)
#                        c: delay in seconds on presentation
#                        d: delay after presentation or in-between tap
########################################################################################################

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
try:
    apds = ColorSensor(i2c)
    apds.enableLightSensor(True)
except:
    pass

rob = Robot()
arm = rob.arm

#### Down / Card Read Position  ########
XPos = 253
YPos = 13
ZPos = 94
########################################

ZTopPos = ZPos + 80
if (ZTopPos > 200):
   ZTopPos = 200
XTopPos =  XPos - 70  
posTop = (XTopPos, YPos, ZTopPos)

i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
apds = ColorSensor(i2c)
apds.enableLightSensor(True)
apds.setAmbientLightGain(3)

tm = TM1640(clk=Pin(33), dio=Pin(32))

tm.tube_display("8888", overFlowText=False)   #displaying ALL LED
print("Card Tapping Test Ready")
ServoDelayTime = 250

arm.set_position(posTop, ServoDelayTime)  #Top Position
time.sleep(1)

def checkLEDColor():
  LEDColorValue = 0     
  vals_r = []
  vals_g = []
  vals_b = []

  #print("Before " + str(vals_r) + ", " + str(vals_g) + ", " + str(vals_b))
  for count in range(250):
	
    r, g, b = apds.readRGBLight()
    #print(str(r) + ", " + str(g) + ", " + str(b))
    vals_r.append(r)
    vals_g.append(g)
    vals_b.append(b)

		# time.sleep_ms(25)
		
  out = (max(vals_r), max(vals_g), max(vals_b))
  print("LED: ",out)
  if max(vals_r) >= 9 and max(vals_g) >  12 and max(vals_r) > max(vals_b):
    tm.tube_display("red")
    LEDColorValue = 1
  elif  max(vals_g) >= 3  and  max(vals_g) > max(vals_b):
    tm.tube_display("grn")
    LEDColorValue = 2
  elif max(vals_b) > 8 and max(vals_b) > max(vals_g) and max(vals_b) > max(vals_r):
    tm.tube_display("blue")
    LEDColorValue = 3
  else:
    tm.tube_display("none")
    LEDColorValue = 0

  # print("LEDRet: ",LEDColorValue)
  # print(str(r) + ", " + str(g) + ", " + str(b))
  return LEDColorValue


def TapCard(NumOfTap = 0, posDist = 0, tapDelay = 1.5, DelayAfter = 4):
  #nozzle.on()
  NumOfGranted = 0
  NumOfDenied = 0
  NumOfInvalid = 0

  tm.tube_display("    ")   # Clears the LED Counter 
  try:
    for i in range(NumOfTap):
      #Card Reading
      ZTopPos = ZPos + 80
      if (ZTopPos > 200):
        ZTopPos = 200
      posTop = (XTopPos, YPos, ZTopPos)
      posDown = (XPos, YPos, ZPos + posDist)

      arm.set_position(posDown, ServoDelayTime)
      print("Tap#:",i+1)
      tm.tube_display(i+1, overFlowText=False)  # Displays counter on LED
      #DelayMsg(1)  ### Delay Time on Card Tap 
      #time.sleep(tapDelay) ### Delay Time on Card Tap
      LEDColorVal = 0
      LEDColorVal = checkLEDColor()
      if(LEDColorVal == 1):
        print("Access Denied")
        NumOfDenied = NumOfDenied + 1
      elif(LEDColorVal == 2):
        print("Access Granted")
        NumOfGranted = NumOfGranted + 1
      elif(LEDColorVal == 3):
        print("LOCKOUT")
      else:
        print("NONE")
        NumOfInvalid = NumOfInvalid + 1

      time.sleep(tapDelay) ### Delay Time on Card Tap

      #top Position
      arm.set_position(posTop, ServoDelayTime)
      #DelayMsg(4)  ### Delay Time at Top)
      time.sleep(DelayAfter) ### Delay After presentation or in-between tap
  except KeyboardInterrupt:
    pass

  #nozzle.off()
  print("\n*** Summary of Test *** ")
  print(" Number of Presentations: ", NumOfTap)
  print(" Number of VALID Access: ", NumOfGranted)
  print(" Number of Denied Access: ", NumOfDenied)
  print(" Number of Invalid Access: ", NumOfInvalid)  
  print(" \n\n")
  arm.set_position(posTop, ServoDelayTime)
  arm.teaching_mode()

def GetCoordinates():
  print('Position 1:', bus_servo.get_position(1)) # Get the position of servo No. 1
  print('Position 2:', bus_servo.get_position(2)) # Get the position of servo No. 2
  print('Position 3:', bus_servo.get_position(3)) # Get the position of servo No. 3

def DelayMsg(ms1):
  time.sleep_ms(ms1 * 1000)
  #print(ms1+"-Sec Delay")

### arm.read_position()