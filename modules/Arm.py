import time
import math
import _thread as thread
from BusServo import BusServo

L0 = 84.0   # Ground to base
L1 = 8.2    # Center of base out to first arm
L2 = 128.0  # Length of first arm
L3 = 138.0  # Length of second arm
L4 = 16.8   # Length of third arm

ORIGIN = (L1 + L3, 0, L0 + L2 - L4)
SERVO_DIRECTION = (1, -1, 1)


class Arm:
    _class_lock = thread.allocate_lock()
    def __init__(self, bus_servo=BusServo(), origin=ORIGIN):
        self.bus_servo = bus_servo
        self.origin = origin

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def pulses_to_joints(self, pulses):
        joints = []
        for i, pulse in enumerate(pulses):
            joint = self.map(pulse, 120, 880, -90, 90)
            joint *= SERVO_DIRECTION[i]
            joints.append(joint)
        return joints

    def joints_to_pulses(self, joints):
        pulses = []
        for i, joint in enumerate(joints):
            joint *= SERVO_DIRECTION[i]
            pulse = self.map(joint, -90, 90, 120, 880)
            pulses.append(int(pulse))
        return pulses

    def forward(self, joints):
        j1, j2, j3 = list(map(math.radians, joints))
        x = (L1 + L2 * math.sin(j2) + L3 * math.cos(j3)) * math.cos(j1)
        y = (L1 + L2 * math.sin(j2) + L3 * math.cos(j3)) * math.sin(j1)
        z = L0 + L2 * math.cos(j2) - L3 * math.sin(j3)

        position = x, y, z
        return position

    def inverse(self, position):
        x, y, z = position

        j1 = math.atan2(y, x)

        l = (x ** 2 + y ** 2) ** 0.5 - L1
        r = (l ** 2 + (z - L0) ** 2) ** 0.5

        num = r ** 2 - L2 ** 2 - L3 ** 2
        den = -2 * L2 * L3
        
        # Check if the argument for acos is out of range
        acos_arg = num / den
        if acos_arg < -1 or acos_arg > 1:
            print("Inverse kinematics error: acos argument out of range")
            return False
        beta = math.acos(acos_arg)
        
        # Check if the argument for asin is out of range
        asin_arg = L3 * math.sin(beta) / r
        if asin_arg < -1 or asin_arg > 1:
            print("Inverse kinematics error: asin argument out of range")
            return False
        alpha = math.asin(asin_arg)

        j2 = math.radians(90) - math.atan2((z - L0), l) - alpha
        j3 = math.radians(90) + j2 - beta

        joints = tuple(map(math.degrees, [j1, j2, j3]))

        return joints

    def pulses_to_position(self, pulses):
        joints = self.pulses_to_joints(pulses)
        position = self.forward(joints)
        return position

    def position_to_pulses(self, position):
        joints = self.inverse(position)
        if not joints:
            print("Failed to calculate inverse kinematics.")
            return False
        pulses = self.joints_to_pulses(joints)
        return pulses

    def read_pulses(self):
        with Arm._class_lock:
            pulses = []
            num_servos = 3
            max_attempts = 3
            for i in range(num_servos):
                for attempt in range(max_attempts):
                    pulse = self.bus_servo.get_position(i + 1)
                    if pulse:
                        pulses.append(pulse)
                        break
                    if attempt == max_attempts - 1:
                        return False
                    time.sleep_ms(5)
                time.sleep_ms(5)

            return pulses

    def read_joints(self):
        pulses = self.read_pulses()
        joints = self.pulses_to_joints(pulses)
        return joints

    def read_position(self):
        pulses = self.read_pulses()
        position = self.pulses_to_position(pulses)
        return position

    def set_servos(self, pulses, duration=2000):
        duration = int(duration)

        if min(pulses) < 0 or max(pulses) > 1000:
            print("Servo pulse out of range. Must be between 0 and 1000.")
            return False

        for i in range(3):
            self.bus_servo.run(i + 1, pulses[i], duration)

        return True

    def set_joints(self, joints, duration=2000):
        j1, j2, j3 = joints

        if j1 < -118 or j1 > 118:
            print("j1 angle out of range. Must be between -118 and 118.")
            return False

        if j2 < -35 or j2 > 90:
            print("j2 angle out of range. Must be between -35 and 90.")
            return False

        if j3 < -4 or j3 > 90:
            print("j1 angle out of range. Must be between -4 and 90.")
            return False

        if j2 - j3 > 63:
            print("j2 and j3 angle combination out of range. j2 - j3 must be less than 63.")
            return False

        pulses = self.joints_to_pulses(joints)
        self.set_servos(pulses, duration)

    def set_position(self, position, duration=2000):
        x, y, z = position

        if math.sqrt(x ** 2 + y ** 2) < 90:
            print("Position out of range. sqrt(x^2 + y^2) must be greater than 90.")
            return False

        joints = self.inverse(position)
        if not joints:
            print("Failed to calculate inverse kinematics.")
            return False
        
        self.set_joints(joints, duration)

    def set_position_with_speed(self, position, speed=0.3):
        old_position = self.read_position()
        distance = math.sqrt(sum([(position[i] - old_position[i]) ** 2 for i in range(0, 3)]))
        duration = distance / max(speed, 0.001)
        self.set_position(position, duration)

    def go_home(self, duration=2000):
        self.set_joints((0, 0, 0), duration)

    def teaching_mode(self):
        for i in range(3):
            self.bus_servo.unload(i + 1)
