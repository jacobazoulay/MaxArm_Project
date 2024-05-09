import time
import _thread as thread
from machine import Pin, PWM
from PWMServo import PWMServo
  

class MultiCardHolder(PWMServo):

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
      raise ValueError("Slot must be integer 0, 1, or 2.")
    time.sleep_ms(1000)
    self.teaching_mode()
  

class SuctionNozzle(PWMServo):
  
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
