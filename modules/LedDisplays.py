from micropython import const
from machine import Pin
import time
import math
# from Robot import Robot

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

# robot_move_horiz = [[0x02, 0x06, 0xce, 0xda, 0xf2, 0xe2, 0xc2, 0xc6, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x06, 0xce, 0xda, 0xf2, 0xe2, 0xc2, 0xc2, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc6, 0xde, 0xfa, 0xe2, 0xc2, 0xc2, 0x02, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xce, 0xfe, 0xf2, 0xc2, 0xc2, 0x02, 0x02, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc2, 0x02, 0x02, 0x02, 0x06, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xf0, 0xfe, 0xce, 0xc2, 0x02, 0x02, 0x02, 0x02, 0x06, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xe0, 0xf8, 0xde, 0xc6, 0x02, 0x02, 0x02, 0x02, 0x02, 0x06, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xe0, 0xf0, 0xd8, 0xce, 0x06, 0x02, 0x02, 0x02, 0x02, 0x02, 0x06, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xe0, 0xf0, 0xd8, 0xcc, 0x06, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x06]]
    
# robot_move_vert  = [[0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc2, 0x02, 0x02, 0x02, 0x06, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc2, 0x04, 0x04, 0x04, 0x0c, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc2, 0x04, 0x04, 0x08, 0x18, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc4, 0x04, 0x08, 0x10, 0x30, 0x00, 0x00, 0x00, 0x00],
#                         [0x00, 0x00, 0xc0, 0xc0, 0xfe, 0xfe, 0xc2, 0xc4, 0x08, 0x10, 0x20, 0x60, 0x00, 0x00, 0x00, 0x00]]


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
        time.sleep_us(TM1640_DELAY)

        self._write_data_cmd()
        self._write_dsp_ctrl()

    def _start(self):
        self.dio.value(0)
        time.sleep_us(TM1640_DELAY)
        self.clk.value(0)
        time.sleep_us(TM1640_DELAY)

    def _stop(self):
        self.dio.value(0)
        time.sleep_us(TM1640_DELAY)
        self.clk.value(1)
        time.sleep_us(TM1640_DELAY)
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
            time.sleep_us(TM1640_DELAY)
            self.clk.value(1)
            time.sleep_us(TM1640_DELAY)
            self.clk.value(0)
            time.sleep_us(TM1640_DELAY)

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

    def write(self, rows):
        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2)
        for row in rows:
            self._write_byte(row)

        self._stop()
        self._write_dsp_ctrl()

    def write_hmsb(self, buf):
        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2)
        for i in range(7, -1, -1):
            self._write_byte(buf[i])

        self._stop()
        self._write_dsp_ctrl()
    
    def set_bit(self, x, y, s):
        self.display_buf[x] = (self.display_buf[x] & (~(0x01 << y))) | (s << y)
    
    def update_display(self, buf = 0):
        if not buf:
          buf = self.display_buf
        self.write(buf)
        self.display_buf = [0] * 16


class LEDDigitDisplay(TM1640):

    def __init__(self, clk, dio, brightness=7):
        super().__init__(clk, dio, brightness)
    
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


class LEDMatrixDisplay(TM1640):

    def __init__(self, clk, dio, brightness=7):
        super().__init__(clk, dio, brightness)

    def bits2byte(self, bit_list):
        if len(bit_list) != 8:
            raise ValueError("Length of bit list must be 8")
        out = 0
        for bit in bit_list:
            out = (out << 1) | bit

        return out

    def map(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def draw_vert_line(self, pos=0):
        if not 0 <= pos <= 15:
            raise ValueError("Vertical line position out of range")
        in_cmd = [0x00] * 16
        in_cmd[pos] = 0xff

        self.write(in_cmd)

    def draw_horiz_line(self, pos=0):
        if not 0 <= pos <= 7:
            raise ValueError("Horizontal line position out of range")
        v_line_bits = [0] * 8
        v_line_bits[pos] = 1
        vert_line = self.bits2byte(v_line_bits)
        in_cmd = [vert_line] * 16

        self.write(in_cmd)
    
    def animate_loading_horiz(self, dur=2000, num_cycles=1):
        for _ in range(num_cycles):
            in_cmd = [0x00] * 16
            for i in range(16):
                in_cmd[i] = 0xff
                self.write(in_cmd)
                time.sleep_ms(dur // 16)

    def robot_start_up_animation(self, dur):
        pass
    
    # def mimic_robot_pos(self, coordinates):
        
    #     x, y, z = coordinates
    #     x_disp = (x**2 + y**2)**0.5
    #     y_disp = z

    #     x_animate = self.map(x_disp, 60, 250, 0, 8)
    #     y_animate = self.map(y_disp, 90, 200, 4, 0)

    #     x_animate = round(max(0, min(8, x_animate)))
    #     y_animate = round(max(0, min(4, y_animate)))

    #     if 140 < x_disp < 180 or y_disp < 150:
    #         frame = robot_move_vert[y_animate]
    #     else:
    #         frame = robot_move_horiz[x_animate]

    #     self.write(frame)

    def draw_line(self, grid, p0, p1):
        x0, y0 = p0
        x1, y1 = p1
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            # Set pixel at current position
            if 0 <= x0 < len(grid) and 0 <= y0 < len(grid[x0]):
                grid[x0][y0] = 1  # You may need to adjust this to match your LED matrix library

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def conv_frame(self, frame):
        out = []
        for row in frame:
            byte_val = self.bits2byte(row)
            out.append(byte_val)
        return out

    def generate_frame(self, angles):
        L1 = 5
        L2 = 6
        ORIG = 5, 1
        ORIG_LEFT = ORIG[0] - 1, ORIG[1]

        _, j2, j3 = angles

        j2 = math.radians(180 - j2)
        j3 = math.radians(-j3)

        p1 = round(ORIG[0] + L1*math.cos(j2)), round(ORIG[1] + L1*math.sin(j2))
        p1_left = p1[0] -1, p1[1]
        p2 = round(p1[0] + L2*math.cos(j3)), round(p1[1] + L2*math.sin(j3))
        p3 = p2[0], p2[1]-1

        grid = [[0] * 8 for _ in range(16)]
        self.draw_line(grid, (2, 0), (7, 0))
        self.draw_line(grid, (2, 1), (7, 1))
        
        self.draw_line(grid, ORIG, p1)
        self.draw_line(grid, ORIG_LEFT, p1_left)
        self.draw_line(grid, p1, p2)
        self.draw_line(grid, p2, p3)

        return grid
    
    def mimic_robot(self, arm: Robot.arm):
        joints = arm.read_angles()
        grid = self.generate_frame(joints)
        frame = self.conv_frame(grid)
        self.write(frame)


def test():
    led_dig_display = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
    for i in range(1000):
        led_dig_display.tube_display(i)


def testMatrix():
    rob = Robot()
    mat = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
    mat.mimic_robot(rob.arm)

def testmat2():
    frames=[[63, 63, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [63, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 192, 192, 254, 254, 194, 194, 2, 2, 2, 6, 0, 0, 0, 0]]
    mat = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
    for frame in frames:
        mat.write(frame)
        time.sleep(0.4)

if __name__ == "__main__":
    testmat2()

