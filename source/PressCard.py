import time
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from Arm import Arm

nozzle = SuctionNozzle()
bus_servo = BusServo() 
arm = Arm(bus_servo)
# = open("InputNum.txt", "r")


if __name__ == '__main__':
    num = 3
    arm.go_home()
    time.sleep_ms(1000)

  #moving to grab the card

    bus_servo.run(1, 501, 250)
    time.sleep_ms(250)

    bus_servo.run(2, 312, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 749, 250)
    time.sleep_ms(250)

    nozzle.on()
    time.sleep_ms(2000)

  #moves the card back to the home position
    arm.go_home()
    time.sleep_ms(1000)

    for i in range(1,num):
  #moves card to the lock
      bus_servo.run(1, 135, 250)
      time.sleep_ms(250)
    
      bus_servo.run(2, 359, 250)
      time.sleep_ms(250)

      bus_servo.run(3, 630, 250)
      time.sleep_ms(2500)
    
  #moves card above the lock
      bus_servo.run(1, 135, 250)
      time.sleep_ms(250)
    
      bus_servo.run(2, 415, 250)
      time.sleep_ms(250)

      bus_servo.run(3, 468, 250)
      time.sleep_ms(3000)
    
  #moves card back home
    arm.go_home()
    
  #places card back to original places
    bus_servo.run(1, 501, 250)
    time.sleep_ms(250)

    bus_servo.run(2, 312, 250)
    time.sleep_ms(250)

    bus_servo.run(3, 749, 500)
    time.sleep_ms(500)

    nozzle.off()
    arm.go_home()
