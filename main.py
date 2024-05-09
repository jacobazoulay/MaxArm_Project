import sys
# Adding /modules directory to PATH to streamline import statements
sys.path.append('/modules')

# Adding this line because somewhere in the frozen modules 'len' is assigned to an integer variable,
# overwriting the builtin function. This causes errors down stream if not corrected here
if isinstance(len, int): del len

import time
import _thread as thread
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
    led_dig_disp.tube_display("----")
    
    
def start_up_animation(rob: Robot):
    rob.LED_mat_disp.robot_start_up_animation()


def reset(rob: Robot):
    thread.start_new_thread(rob.rob_reset_arm, ())
    thread.start_new_thread(buz_led_reset, [rob])
    thread.start_new_thread(display_welcome_msg, [rob])
    thread.start_new_thread(start_up_animation, [rob])

def play():
    from LedDisplays import SnakeGame
    game = SnakeGame()
    game.playGame()

if __name__ == "__main__":
    rob = Robot(run_startup=False, mimic=True)
    reset(rob)
    time.sleep(5)
    rob.mimic_position(True)
