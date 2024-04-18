import time
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from Arm import Arm

nozzle = SuctionNozzle()
bus_servo = BusServo() 
arm = Arm(bus_servo)
height = [395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409]
new = 0


if __name__ == '__main__':
  arm.go_home()
  time.sleep_ms(1000)

#moving to grab the card


  bus_servo.run(1, 501, 500)
  time.sleep_ms(1000)

  bus_servo.run(2, 312, 500)
  time.sleep_ms(1000)

  bus_servo.run(3, 749, 500)
  time.sleep_ms(1000)

  nozzle.on()
  time.sleep_ms(2000)

#moves the card back to the home position
  arm.go_home()
  time.sleep_ms(1000)

#moves card to the lock
  bus_servo.run(1, 135, 500)
  time.sleep_ms(500)
  
  bus_servo.run(2, 359, 500)
  time.sleep_ms(500)

  bus_servo.run(3, 630, 500)
  time.sleep_ms(2500)
  
#moves card above the lock

  bus_servo.run(1, 135, 500)
  time.sleep_ms(500)

  bus_servo.run(2, 415, 500)
  time.sleep_ms(500)

  bus_servo.run(3, 468, 500)
  time.sleep_ms(1750)
  
#moves card back home
  arm.go_home()
  
#places card back to original places
  bus_servo.run(1, 501, 500)
  time.sleep_ms(1000)

  bus_servo.run(2, 312, 500)
  time.sleep_ms(1000)

  bus_servo.run(3, 749, 500)
  time.sleep_ms(1000)

  nozzle.off()
  arm.go_home()

