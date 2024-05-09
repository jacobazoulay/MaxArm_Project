from machine import Pin, Timer
from machine import PWM
import time


class PWMServo:
    def __init__(self, pin=15, min_angle=-90, max_angle=90, freq=50):
        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_duty = int(freq * 0.46)
        self.max_duty = int(freq * 2.56)
        self.freq = freq
        self.pwm = PWM(Pin(pin), freq=freq)

    def angle_to_duty(self, angle):
        # Map angle to duty cycle within the specified range
        return int(((angle - self.min_angle) / (self.max_angle - self.min_angle)) * (self.max_duty - self.min_duty) + self.min_duty)

    def duty_to_angle(self, duty):
        # Map duty cycle to angle within the specified range
        return int((duty - self.min_duty) / (self.max_duty - self.min_duty) * (self.max_angle - self.min_angle) + self.min_angle)

    def set_angle(self, angle):
        # Clip angle to be within the range of min_angle and max_angle
        angle = max(self.min_angle, min(angle, self.max_angle))
        
        duty = self.angle_to_duty(angle)
        self.pwm.duty(duty)

    def move_to(self, end_angle, duration_ms, steps=100):
        start_angle = self.get_current_angle()
        angle_difference = end_angle - start_angle
        step_angle = angle_difference / steps
        delay = duration_ms // steps
      
        for _ in range(steps):
            start_angle += step_angle
            self.set_angle(start_angle)
            time.sleep_ms(delay)
    
    def move_to_with_speed(self, end_angle, speed_deg_per_s=375):
        start_angle = self.get_current_angle()
        angle_difference = abs(end_angle - start_angle)
        duration_ms = int(angle_difference / (speed_deg_per_s / 1000))
        self.move_to(end_angle, duration_ms)
        time.sleep_ms(duration_ms)
        self.teaching_mode()

    def get_current_angle(self):
        duty = self.pwm.duty()
        return self.duty_to_angle(duty)
      
    def teaching_mode(self):
        self.pwm.duty(0)
