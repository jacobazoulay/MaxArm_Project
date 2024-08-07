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
    _class_lock = thread.allocate_lock()
    _mimic = None
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
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

        try:
            i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
            self.RGB_sensor = ColorSensor(i2c)
            self.RGB_sensor.enableLightSensor(True)
            self.RGB_sensor.setAmbientLightGain(3)
        except OSError:
            print("Color sensor not found. Functionality limited.")
            self.RGB_sensor = None

        self.RGB_last_reading = "no reading"

        self.mimic_position(mimic)

        if run_startup:
            self.reset()

    def __del__(self):
        self.mimic_position(False)
        time.sleep_ms(100)
        
    def reset(self, reset_seg_disp=True):
        self.arm.go_home()
        time.sleep_ms(2000)
        if reset_seg_disp: self.LED_seg_disp.tube_display("----")
        self.arm.teaching_mode()
        self.end_effector.set_card(1)

    def mimic_position(self, mimicFlag):
        if mimicFlag is False:
            Robot._mimic = False
            return
        if mimicFlag is True:
            if Robot._class_lock.locked():
                return
            thread.start_new_thread(self._mimic_loop, ())

    def _mimic_loop(self):
        with Robot._class_lock:
            Robot._mimic = True
            while Robot._mimic:
                self.LED_mat_disp.mimic_robot(self.arm)
            self.LED_mat_disp.update_display()

    def readRGB(self, timeout):
        self.thread_running = True
        if self.RGB_sensor is None:
            self.RGB_last_reading = "No color sensor detected"
            self.thread_running = False
            return

        thresh = 250
        MIN_CONSECUTIVE_TO_BE_VALID = 9
        meas = ['start']
        meas_temp = [None] * MIN_CONSECUTIVE_TO_BE_VALID

        start_time = time.time()
        timeout_duration = (timeout / 1000) * 0.8

        while time.time() - start_time < timeout_duration:
            r, g, b = self.RGB_sensor.readRGBLight()
            # print("(" + str(r) + ", " + str(g) + ", " + str(b) + "),")
            if max(r, g, b) > thresh:  # if the light is on
                if r > g and r > b and g > 0.33 * r:
                    meas_temp.append('y')
                elif r > g and r > b and g <= 0.33 * r:
                    meas_temp.append('r')
                elif g > r and g > b * 1.2:
                    meas_temp.append('g')
                else:
                    meas_temp.append('b')
            else:  # if the light is off
                    meas_temp.append('n')
                    
            meas_temp.pop(0)

            if len(set(meas_temp)) == 1 and meas[-1] != meas_temp[-1]:
                meas.append(meas_temp[-1])

        color_decode = {('start', 'n', 'r', 'n'): 'declined',
                        ('start', 'y', 'n', 'r', 'n'): 'declined',
                        ('start', 'n', 'r', 'y', 'n'): 'declined',
                        ('start', 'n', 'y', 'r', 'n'): 'declined',
                        ('start', 'n', 'r', 'n', 'r', 'n'): 'declined',

                        ('start', 'n', 'g', 'n'): 'granted',
                        ('start', 'y', 'n', 'g', 'n'): 'granted',
                        ('start', 'n', 'r', 'n', 'g', 'n'): 'granted',

                        ('start', 'n', 'r', 'b', 'n'): 'lockout',
                        ('start', 'n', 'r', 'n', 'b', 'n'): 'lockout',
                        ('start', 'n', 'r', 'n', 'r', 'b', 'n'): 'lockout',
                        ('start', 'n', 'r', 'y', 'b', 'n'): 'lockout',
                        ('start', 'n', 'r', 'n', 'r', 'n', 'b', 'n'): 'lockout',
                        ('start', 'n', 'r', 'b', 'g', 'n'): 'lockout',
                        ('start', 'n', 'r', 'n', 'r', 'y', 'b', 'n'): 'lockout',

                        ('start', 'n', 'y'): 'waiting',
                        ('start', 'n', 'y', 'n'): 'waiting',
                        ('start', 'n', 'r', 'y'): 'waiting',

                        ('start', 'n'): 'no reading'}

        if tuple(meas) in color_decode:
            result = color_decode[tuple(meas)]
        else:
            result = "unrecognized"
        self.RGB_last_reading = result

        self.LED_mat_disp.display_reader_result(result)
        print(meas)
        self.thread_running = False

    def presentCard(self, slot, num=1, press_dur=1500, retract_dur=2000):
        prev_mimic_flag = self._mimic
        if self.RGB_sensor is not None:  # If no rgb sensor, no readRGB is displayed on Matrix, so just show robot mimic position
            self.mimic_position(False)

        self.arm.set_position((115, 0, 190), 400)
        self.LED_seg_disp.tube_display("crd" + str(slot + 1))
        self.end_effector.set_card(slot)

        for i in range(num):
            s = ("crd" + str(slot + 1)) if (num <= 3) else (i + 1)
            self.LED_seg_disp.tube_display(s)

            thread.start_new_thread(self.readRGB, [press_dur + retract_dur])

            self.arm.set_position((213, 0, 180), 400)
            time.sleep_ms(press_dur)
            self.arm.set_position((115, 0, 190), 400)
            time.sleep_ms(retract_dur)
            while self.thread_running:
                time.sleep_ms(100)
            print("Presentation Number: {}      Reading: {}      Card Slot: {} ".format(i + 1, self.RGB_last_reading, slot))

        self.arm.teaching_mode()
        if self.RGB_sensor is not None:
            self.mimic_position(prev_mimic_flag)


if __name__ == "__main__":
    rob = Robot()
    rob.presentCard(1, num=1)
