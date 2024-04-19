import sys
# Adding /modules directory to PATH to streamline import statements
sys.path.append('/modules')

import time
from machine import Pin
import _thread as thread
from LedDisplays import LEDDigitDisplay
from Buzzer import Buzzer
from Led import LED
from Robot import Robot


def buz_led_reset(rob: Robot):
    buz = rob.buz
    led = rob.led
    for i in range(3):
        buz.on()
        led.on()
        time.sleep_ms(250)
        buz.off()
        led.off()
        time.sleep_ms(250)

def display_welcome_msg(rob: Robot):
    led_dig_disp = rob.LED_seg_disp
    led_dig_disp.tube_display("    Hello Robot", scroll_speed_ms=150)

def reset():
    rob = Robot()
    
    thread.start_new_thread(rob.rob_reset, ())
    thread.start_new_thread(buz_led_reset, [rob])
    thread.start_new_thread(display_welcome_msg, [rob])
    

if __name__ == "__main__":
    reset()

