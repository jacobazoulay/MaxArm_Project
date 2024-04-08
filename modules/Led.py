from machine import Pin, PWM
import time


class LED:
  
  def __init__(self, io=26, hz=1000):
    self.p0 = Pin(io)
    self.led = PWM(self.p0)
    self.led.freq(hz)
    self.hz = hz
    self.init_flag = True

  def on(self):
    if not self.init_flag:
      self.led.init()
      self.init_flag = True
    self.led.duty(0)
  
  def off(self):
    if self.init_flag:
      self.led.deinit()
      self.init_flag = False
    self.p0.on()
    
  def pwm(self, brightness=50):
    self.on()
    hz = int(self.map(brightness, 0, 100, 1023, 0))
    self.led.duty(hz)
  
  def map(self, x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


if __name__ == "__main__":
  led = LED()
  for i in range(10):
    led.on()
    time.sleep_ms(300)
    led.off()
    time.sleep_ms(300)


