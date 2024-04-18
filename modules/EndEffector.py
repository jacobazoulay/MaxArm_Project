import time
import _thread as thread
from machine import Pin, PWM
from PWMServo import PWMServo


class EndEffector():
  
  def __init__(self):
    self.pwm_servo = PWMServo()
  
  def set_angle(self, angle=0, duration=1):
    pulse = self.map(angle, -90, 90, 460, 2500)

    pulse = 460 if pulse < 460 else pulse
    pulse = 2500 if pulse > 2500 else pulse
    self.pwm_servo.run(1, pulse, duration)

  def map(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  

class MultiCardHolder(EndEffector):

  def __init__(self):
    super().__init__()

  def set_card(self, slot):
    if slot == 0:
      self.set_angle(-90)
    elif slot == 1:
      self.set_angle(0)
    elif slot == 2:
      self.set_angle(90)
    
    else:
      raise ValueError("Slot must be integer 1, 2, or 3.")
  

class SuctionNozzle(EndEffector):
  
  def __init__(self, pump_io=[21,19], valve_io=[18,5], hz=1000):
    super().__init__()
    self.pump_f = PWM(Pin(pump_io[0]))
    self.pump_b = PWM(Pin(pump_io[1]))
    self.valve_f = PWM(Pin(valve_io[0]))
    self.valve_b = PWM(Pin(valve_io[1]))
    self.pump_f.freq(hz)
    self.pump_b.freq(hz)
    self.valve_f.freq(hz)
    self.valve_b.freq(hz)
    self.hz = hz

    self.nozzle_st = False
    
  def on(self):
    if not self.nozzle_st:
      self.pump_f.duty(self.hz)
      self.pump_b.duty(0)
      self.valve_f.duty(0)
      self.valve_b.duty(0)
      self.nozzle_st = True
  
  def _off(self):
    if self.nozzle_st:
      self.valve_f.duty(self.hz)

      self.valve_b.duty(0)
      self.pump_f.duty(0)
      self.pump_b.duty(0) 
      time.sleep_ms(1000)
      self.valve_f.duty(0)
      self.valve_b.duty(0)
      self.nozzle_st = False
  
  def off(self):
    thread.start_new_thread(self._off, ())

