import time
import _thread as thread
from machine import Pin, I2C
from Arm import Arm
from EndEffector import SuctionNozzle, MultiCardHolder
from LedDisplays import LEDDigitDisplay, LEDMatrixDisplay
from Buzzer import Buzzer
from Led import LED
from ColorSensor import ColorSensor


class Robot:
  
  def __init__(self, nozzle=False, mimic=True):
    if nozzle:
      self.nozzle = SuctionNozzle()
    else:
      self.end_effector = MultiCardHolder()

    self.arm = Arm()
    self.buz = Buzzer()
    self.led = LED()

    self.LED_seg_disp = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
    self.LED_mat_disp = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
    
    i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
    self.RGB_sensor = ColorSensor(i2c)
    self.RGB_sensor.enableLightSensor(True)
    self.RGB_sensor.setAmbientLightGain(3)
    
    self.LED_mat_disp.robot_start_up_animation()
    
    self.mimic = mimic
    self.mimic_position(self.mimic)
  
  def rob_reset(self):
    self.arm.go_home()
    time.sleep_ms(2000)
    self.arm.teaching_mode()
    self.end_effector.set_angle(0)
  
  def mimic_position(self, mimicFlag):
    self.mimic = mimicFlag
    if self.mimic:
      thread.start_new_thread(self._mimic_loop, ())
  
  def _mimic_loop(self):
    time.sleep(1)
    while self.mimic:
      self.LED_mat_disp.mimic_robot(self.arm)
      time.sleep_ms(200)
    self.LED_mat_disp.update_display()

  def test(self):
    self.arm.set_position_with_speed((0, 130, 200), 0.3)
    for i in range(3):
      self.end_effector.set_card(i)
      time.sleep_ms(500)
      self.arm.set_position_with_speed((0, 230, 190), 0.3)
      time.sleep_ms(1500)
      self.arm.set_position_with_speed((0, 130, 200), 0.3)
      time.sleep_ms(2000)
    rob.arm.teaching_mode()


if __name__ == "__main__":
  rob = Robot()
  rob.test()
  
  























