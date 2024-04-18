import time
from SuctionNozzle import SuctionNozzle
from BusServo import BusServo
from Arm import Arm

nozzle = SuctionNozzle()
bus_servo = BusServo() 
arm = Arm(bus_servo)


if __name__ == '__main__':
  nozzle.on()
  for i in range(0,1):
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
  nozzle.off()
  

