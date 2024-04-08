import sys
# Adding /modules directory to PATH to streamline import statements
sys.path.append('/modules')

from RobotControl import RobotControl
import time
from TM1640 import TM1640
from machine import Pin
from Buzzer import Buzzer
from Led import LED
import _thread as thread


def rob_reset():
    rob = RobotControl()

    rob.arm.go_home()
    time.sleep_ms(2000)
    rob.arm.teaching_mode()
    rob.nozzle.on()
    rob.nozzle.off()
    rob.nozzle.set_angle(0)

def buz_led_reset():
    buz = Buzzer()
    led = LED()
    for i in range(3):
        buz.on()
        led.on()
        time.sleep_ms(250)
        buz.off()
        led.off()
        time.sleep_ms(250)

def display_welcome_msg():
    tm = TM1640(clk=Pin(33), dio=Pin(32))
    tm.tube_display("    Hello Robot", scroll_speed_ms=150)


def reset():
    thread.start_new_thread(rob_reset, ())
    thread.start_new_thread(buz_led_reset, ())
    thread.start_new_thread(display_welcome_msg,())
    

if __name__ == "__main__":
    reset()