from machine import Pin
import time


class LED:
  
  def __init__(self, io=26):
    self.p0 = Pin(io, Pin.OUT)

  def on(self):
    self.p0.off()
  
  def off(self):
    self.p0.on()


if __name__ == "__main__":
  led = LED()
  for i in range(10):
    led.on()
    time.sleep_ms(300)
    led.off()
    time.sleep_ms(300)
