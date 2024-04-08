
from micropython import const
from machine import Pin
from time import sleep_us
import time

TM1640_CMD1 = const(64)  # 0x40 data command
TM1640_CMD2 = const(192) # 0xC0 address command
TM1640_CMD3 = const(128) # 0x80 display control command
TM1640_DSP_ON = const(8) # 0x08 display on
TM1640_DELAY = const(10) # 10us delay between clk/dio pulses


tube_font = {'0':0x3f,'1':0x06,'2':0x5b,'3':0x4f,'4':0x66,'5':0x6d,'6':0x7d,'7':0x07,'8':0x7f,'9':0x6f}
tube_font_letters = {
    'A': 0x77, 'B': 0x7C, 'C': 0x39, 'D': 0x5E, 'E': 0x79, 'F': 0x71,
    'G': 0x3D, 'H': 0x76, 'I': 0x06, 'J': 0x1E, 'K': 0x75, 'L': 0x38,
    'M': 0x37, 'N': 0x54, 'O': 0x3F, 'P': 0x73, 'Q': 0x67, 'R': 0x50,
    'S': 0x6D, 'T': 0x78, 'U': 0x3E, 'V': 0x1C, 'W': 0x2A, 'X': 0x76,
    'Y': 0x6E, 'Z': 0x5B, '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f,
    '4': 0x66, '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, "_": 0x08
}


class TM1640(object):
    # Library for LED matrix display modules based on the TM1640 LED driver.
    def __init__(self, clk, dio, brightness=7):
        self.clk = clk
        self.dio = dio
        self.display_buf = [0] * 16

        if not 0 <= brightness <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = brightness

        self.clk.init(Pin.OUT, value=0)
        self.dio.init(Pin.OUT, value=0)
        sleep_us(TM1640_DELAY)

        self._write_data_cmd()
        self._write_dsp_ctrl()

    def _start(self):
        self.dio.value(0)
        sleep_us(TM1640_DELAY)
        self.clk.value(0)
        sleep_us(TM1640_DELAY)

    def _stop(self):
        self.dio.value(0)
        sleep_us(TM1640_DELAY)
        self.clk.value(1)
        sleep_us(TM1640_DELAY)
        self.dio.value(1)

    def _write_data_cmd(self):
        # automatic address increment, normal mode
        self._start()
        self._write_byte(TM1640_CMD1)
        self._stop()

    def _write_dsp_ctrl(self):
        # display on, set brightness
        self._start()
        self._write_byte(TM1640_CMD3 | TM1640_DSP_ON | self._brightness)
        self._stop()

    def _write_byte(self, b):
        for i in range(8):
            self.dio.value((b >> i) & 1)
            sleep_us(TM1640_DELAY)
            self.clk.value(1)
            sleep_us(TM1640_DELAY)
            self.clk.value(0)
            sleep_us(TM1640_DELAY)

    def brightness(self, val=None):
        # Set the display brightness 0-7.
        # brightness 0 = 1/16th pulse width
        # brightness 7 = 14/16th pulse width
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")

        self._brightness = val
        self._write_data_cmd()
        self._write_dsp_ctrl()

    def write(self, rows, pos=0):
        if not 0 <= pos <= 3:
            raise ValueError("Position out of range")

        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2 | pos)
        for row in rows:
            self._write_byte(row)

        self._stop()
        self._write_dsp_ctrl()

    def write_int(self, int, pos=0, length=8):
        self.write(int.to_bytes(length, 'big'), pos)

    def write_hmsb(self, buf, pos=0):
        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2 | pos)
        for i in range(7-pos, -1, -1):
            self._write_byte(buf[i])

        self._stop()
        self._write_dsp_ctrl()
    
    def set_bit(self, x, y, s):
        self.display_buf[x] = (self.display_buf[x] & (~(0x01 << y))) | (s << y)

    def tube_display_int(self, num, overFlowText=True):
        s = str(num)
        if len(s) > 4 and overFlowText:
            self.tube_display_alpha("_OF_")
            return
        buf = [tube_font[c] for c in s[-4:]] 
        self.display_buf = buf
        if len(buf) < 4:
            buf_zero = [0] * (4 - len(buf))
            buf_zero.extend(buf)
            self.display_buf = buf_zero
        self.update_display()
    
    def tube_display_float(self, num, overFlowText=True):
        s = "{:0.1f}".format(num) 
        if len(s) > 5 and overFlowText:
            self.tube_display_alpha("_OF_")
            return
        buf = []
        for c in s[-5:]:
            if c in tube_font:
                buf.append(tube_font[c])
            else:
                if c == '.': 
                    buf[-1] = buf[-1] | 0x80
        self.display_buf = buf
        if len(buf) < 4: 
            buf_zero = [0] * (4 - len(buf))
            buf_zero.extend(buf)
            self.display_buf = buf_zero
        self.update_display()
        
    def _tube_display_alpha_single(self, s):
        s = str(s).upper()
        s = s[:4]
        if len(s) <= 4:
            s = s + " " * (4 - len(s))
        buf = [tube_font_letters[c] for c in s]
        self.display_buf = buf
        self.update_display()
    
    def tube_display_alpha(self, s, scroll_speed_ms=350):
        if len(s) <=4:
            self._tube_display_alpha_single(s)
        else:
            for i in range(len(s)+ 1):
                sec = s[i:i+4]
                self._tube_display_alpha_single(sec)
                time.sleep_ms(scroll_speed_ms)
    
    def tube_display(self, s, scroll_speed_ms=350, overFlowText=True):
        if isinstance(s, int):
            self.tube_display_int(s, overFlowText)
        elif isinstance(s, float):
            self.tube_display_float(s, overFlowText)
        elif isinstance(s, str):
            self.tube_display_alpha(s, scroll_speed_ms)
        else:
            raise TypeError("Argument must be an integer, float, or string")
    
    def tube_display_flash(self, s, num_flash=10, flash_speed=350):
        if isinstance(s, str) and len(s) > 4:
            s = s[:4]
        for i in range(num_flash):
            self.tube_display(s)
            time.sleep_ms((flash_speed * 3) // 4)
            self.update_display()
            time.sleep_ms((flash_speed * 1) // 4)
        self.tube_display(s)
    
    def update_display(self, buf = 0):
        if not buf:
          buf = self.display_buf
        self.write(buf)
        self.display_buf = [0] * 16

def cycle7SegDisp():
	tm = TM1640(clk=Pin(33), dio=Pin(32))
	tm.update_display()
	tm.brightness(5)
	for i in range(9000, 11000):
		tm.tube_display(i, overFlowText=False)

if __name__ == "__main__":
    # tm = TM1640(clk=Pin(33), dio=Pin(32))
    # tm.update_display()
    # tm.tube_display("Hello World")
    cycle7SegDisp()

    pass

