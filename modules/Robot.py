# Adding this line because somewhere in the frozen modules 'len' is assigned to an integer variable when reconnecting to the COM port,
# overwriting the builtin function. This causes errors down stream if not corrected here
if isinstance(len, int): del len

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
  
  def __init__(self, nozzle=False, run_startup=True, mimic=True):
    self.buz = Buzzer()
    self.led = LED()
    
    if nozzle:
      self.end_effector = SuctionNozzle()
    else:
      self.end_effector = MultiCardHolder()

    self.arm = Arm()
    
    self.LED_seg_disp = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
    self.LED_mat_disp = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
    
    i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
    self.RGB_sensor = ColorSensor(i2c)
    self.RGB_sensor.enableLightSensor(True)
    self.RGB_sensor.setAmbientLightGain(3)
    
    self.mimic = mimic
    
    if run_startup:
      self.rob_reset()
  
  def rob_reset(self):
      self.rob_reset_arm()
      self.LED_seg_disp.tube_display("----")
      self.mimic_position(self.mimic)
  
  def rob_reset_arm(self):
    self.arm.go_home()
    time.sleep_ms(2000)
    self.arm.teaching_mode()
    self.end_effector.move_to_with_speed(0)
    self.end_effector.teaching_mode()
  
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
  