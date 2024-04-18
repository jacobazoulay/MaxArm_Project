#########################################################################################################################
# Systems Automation - MaxArm Python Scripting
# Copyright(R) ASSA ABLOY     - Joel Albarracin / Jacob Azoulay / Dannylo Correria 
#                               21 March 2024
# 
# Python Scripting for MaxArm on Presenting Card with LED Counter 
# 
#########################################################################################################################
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

rob = Robot()
arm = rob.arm
posTop = (220, 6, 182)
posDown = (221, -9, 26)
deniedCard = (158, -104, 2)
accessCard = (221, -101, 5)
betweenPos = (173, -101, 52)
Cards = [accessCard, deniedCard]

tm = TM1640(clk=Pin(33), dio=Pin(32))

tm.tube_display("8888")
print("Card Tapping Test Ready")
ServoDelayTime = 250

arm.set_position(posTop, ServoDelayTime)  #Top Position

color = ""

def checkColor():
  global color
  i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
  apds = ColorSensor(i2c)
  apds.enableLightSensor(True)

  tm = TM1640(clk=Pin(33), dio=Pin(32))


  for i in range(100):
  
    r, g, b = apds.readRGBLight()

    if r > 25 and r > g and r > b:
      tm.tube_display("red")
      color = "Access Denied"
    elif g > 25 and g > r and g > b:
      tm.tube_display("grn")
      color = "Access Granted"
    elif b > 25 and b > g and b > r:
      tm.tube_display("blue")
    else:
      tm.tube_display("none")
    # time.sleep_ms(25)
    
    #print(str(r) + ", " + str(g) + ", " + str(b))

    #time.sleep(0.5)

g = 0

def TapCard(NumOfTap = 0):
  global color
  global g
  global h
  for i in range(2):
    arm.set_position(betweenPos, ServoDelayTime)
    time.sleep(.5)
    arm.set_position(Cards[g], ServoDelayTime)
    time.sleep(1)
    nozzle.on()
    time.sleep(.5)
    arm.set_position(posTop, 350)
    time.sleep(1)
    tm.tube_display("    ")   # Clears the LED Counter 
    for i in range(NumOfTap):
      #Card Reading
      arm.set_position(posDown, ServoDelayTime)
      print("Tap#:",i+1)
      checkColor()
      print(color)
      time.sleep(1)

      #tm.tube_display(i+1)  # Displays counter on LED
      #DelayMsg(1)  ### Delay Time on Card Tap 

      #top Position
      arm.set_position(posTop, ServoDelayTime)
      DelayMsg(3)  ### Delay Time at Top)
      h =+ 1

    time.sleep(1)
    arm.set_position(Cards[g], ServoDelayTime)
    time.sleep(1)
    g =+ 1
    nozzle.off()
        

  nozzle.off()
  arm.set_position(posTop, ServoDelayTime)
  g = 0

def GetCoordinates():
  print('Position 1:', bus_servo.get_position(1)) # Get the position of servo No. 1
  print('Position 2:', bus_servo.get_position(2)) # Get the position of servo No. 2
  print('Position 3:', bus_servo.get_position(3)) # Get the position of servo No. 3

def DelayMsg(ms1):
  time.sleep_ms(ms1 * 1000)
  #print(ms1+"-Sec Delay")


def CardDisTest():
  global color
  global h
  global difpos
  difpos = ['26', '27', '28', '29', '30']
  h = 0
  for i in range(2):
    arm.set_position(betweenPos, ServoDelayTime)
    time.sleep(.5)
    arm.set_position(accessCard, ServoDelayTime)
    time.sleep(1)
    nozzle.on()
    time.sleep(.5)
    arm.set_position(posTop, 350)
    time.sleep(1)
    tm.tube_display("    ")   # Clears the LED Counter 
    for i in range(difpos):
      arm.set_position(posTop, ServoDelayTime)
      
      #Card Reading
      arm.set_position((221, -9, int(difpos[h])), ServoDelayTime)
      h =+ 1
      print("Tap#:",i+1)
      checkColor()
      print(color)
      time.sleep(1)

      #tm.tube_display(i+1)  # Displays counter on LED
      #DelayMsg(1)  ### Delay Time on Card Tap 

      #top Position
      
      #DelayMsg(3)  ### Delay Time at Top)
  
    time.sleep(1)
    arm.set_position(accessCard, ServoDelayTime)
    time.sleep(1)        

  nozzle.off()
  arm.set_position(posTop, ServoDelayTime)
  h = 0