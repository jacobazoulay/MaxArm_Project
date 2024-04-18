import sys
# Adding /modules directory to PATH to streamline import statements
sys.path.append('/modules')

import time
from machine import Pin
import _thread as thread
from LedDisplays import LEDDigitDisplay, LEDMatrixDisplay
from Buzzer import Buzzer
from Led import LED
from Robot import Robot


def rob_reset():
    rob = Robot()

    rob.arm.go_home()
    time.sleep_ms(2000)
    rob.arm.teaching_mode()
    rob.end_effector.set_angle(0)

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
    led_dig_disp = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
    led_dig_disp.tube_display("    Hello Robot", scroll_speed_ms=150)

def display_welcome_animation():
    led_mat_disp = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
    led_mat_disp.animate_loading_horiz()
    led_mat_disp.update_display()


def reset():
    thread.start_new_thread(rob_reset, ())
    thread.start_new_thread(buz_led_reset, ())
    thread.start_new_thread(display_welcome_msg,())
    thread.start_new_thread(display_welcome_animation,())
    

if __name__ == "__main__":
    reset()
    rob = Robot()
    while True:
        rob.mimic_position()