import time
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from Arm import Arm


def main():

  nozzle = SuctionNozzle()
  bus_servo = BusServo() 
  arm = Arm(bus_servo)
  height = [395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409]
  new = 0

  arm.go_home()
  time.sleep_ms(5000)

  #moving to grab the card

  bus_servo.run(1, 498, 1000)
  time.sleep_ms(1000)

  bus_servo.run(2, 311, 1000)
  time.sleep_ms(1000)

  bus_servo.run(3, 750, 1000)
  time.sleep_ms(1000)

  nozzle.on()
  time.sleep_ms(2000)

  #moves the card back to the home position
  arm.go_home()
  time.sleep_ms(3000)

  #loops throught the different hieghts
  for num in height:
    #loops the card to lock process for multiple tests
    for i in range(1, 2):
      #moves the card to the lock
      bus_servo.run(1, 180, 1000)
      time.sleep_ms(1000)

      bus_servo.run(2, height[new], 1000)
      time.sleep_ms(1000)

      new += 1

      bus_servo.run(3, 750, 1000)
      time.sleep_ms(3500)

      #moves the card above the lock
      bus_servo.run(1, 168, 500)
      time.sleep_ms(500)	

      bus_servo.run(2, 459, 500)
      time.sleep_ms(1000)

      bus_servo.run(3, 549, 1000)
      time.sleep_ms(4000)



  #moves the card back to the home position
  arm.go_home()
  time.sleep_ms(1000)

  #moving to place the card back
  bus_servo.run(1, 498, 1000)
  time.sleep_ms(1000)

  bus_servo.run(2, 328, 1000)
  time.sleep_ms(1000)

  bus_servo.run(3, 765, 1000)
  time.sleep_ms(1000)
  
  #drops card
  nozzle.off()

  arm.go_home()


if __name__ == '__main__':
  main()