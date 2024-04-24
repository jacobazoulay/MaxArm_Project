import time
import _thread as thread
from machine import Pin, PWM


class Buzzer:
  
  def __init__(self, io=27, freq=2500):
    self.buzzer = PWM(Pin(io), freq=freq, duty=0)
    self.duty = 18
    self.freq = freq
    self.freq_old = 0
    
  def on(self):
    self.freq_old = self.buzzer.freq()
    self.buzzer.freq(self.freq)
    self.buzzer.duty(self.duty)
  
  def off(self):
    self.buzzer.freq(self.freq_old)
    self.buzzer.duty(0)
  
  def set_volume(self, level=15):
    hz = int(self.map(level, 0, 100, 0, 350))
    self.duty = hz
  
  def map(self, x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  

if __name__ == "__main__":
  buz = Buzzer()
  for i in range(10):
    buz.on()
    time.sleep_ms(300)
    buz.off()
    time.sleep_ms(300)
    