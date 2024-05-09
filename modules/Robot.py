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
        self.mimic = mimic

        if run_startup:
            self.rob_reset()

    def rob_reset(self):
        self.rob_reset_arm()
        self.LED_seg_disp.tube_display("----")
        self.mimic_position(self.mimic)

    def rob_reset_arm(self):
        self.arm.go_home()
        time.sleep_ms(2000)
        self.arm.teaching_mode()
        self.end_effector.set_card(1)

    def mimic_position(self, mimicFlag):
        self.mimic = mimicFlag
        if self.mimic:
            thread.start_new_thread(self._mimic_loop, ())

    def _mimic_loop(self):
        time.sleep(1)
        while self.mimic:
            self.LED_mat_disp.mimic_robot(self.arm)
            time.sleep_ms(200)
        self.LED_mat_disp.update_display()

    def readRGB(self, timeout):
        if self.RGB_sensor is None:
            self.RGB_last_reading = "No color sensor detected"
            return
        low = self.RGB_sensor.readRGBLight()
        thresh = 2 * max(low[0], low[1], low[2])
        meas = ['n']
        has_turned_on = False

        now = time.time()
        while time.time() - now < (timeout / 1000) * 0.9:
            rgb = self.RGB_sensor.readRGBLight()
            if rgb[0] > thresh or rgb[1] > thresh or rgb[2] > thresh:
                has_turned_on = True
                if rgb[0] > rgb[1] and rgb[0] > rgb[2] and meas[-1] != 'r':
                    meas.append('r')
                elif rgb[1] > rgb[0] and rgb[1] > rgb[2] and meas[-1] != 'g':
                    meas.append('g')
                elif rgb[2] > rgb[0] and rgb[2] > rgb[1] and meas[-1] != 'b':
                    meas.append('b')
            else:
                if has_turned_on:
                    break

        color_decode = {'r': 'declined',
                        'g': 'granted',
                        'b': 'lockout',
                        'n': 'no reading'}

        result = color_decode[meas[-1]]
        self.RGB_last_reading = result

        self.LED_mat_disp.display_reader_result(result)
    
    def presentCard(self, slot, num=1, press_dur=1500, retract_dur=2000):
        if self.RGB_sensor is not None: #If no rgb sensor, no readRGB is displayed on Matrix, so just show robot mimic position
            self.mimic_position(False)
            
        self.arm.set_position_with_speed((0, 130, 190), 0.3)
        self.LED_seg_disp.tube_display("crd" + str(slot + 1))
        self.end_effector.set_card(slot)
        
        for i in range(num):
            s = ("crd" + str(slot + 1)) if (num <= 3) else (i + 1)
            self.LED_seg_disp.tube_display(s)
            
            thread.start_new_thread(self.readRGB, [press_dur + retract_dur])
            
            self.arm.set_position_with_speed((0, 230, 180), 0.3)
            time.sleep_ms(press_dur)
            self.arm.set_position_with_speed((0, 130, 190), 0.3)
            time.sleep_ms(retract_dur)
            print("Presentation Number: {}      Reading: {}".format(i+1, self.RGB_last_reading))
            
        self.arm.teaching_mode()
        self.mimic_position(True)


if __name__ == "__main__":
    rob = Robot()
    rob.presentCard(1, num=1)