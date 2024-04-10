from machine import Pin, Timer
from HiwonderV2 import PWM#该PWM的duty范围0~16383
import time

MAX_DUTY = 16383



# Function to control electromagnet strength
def set_magnet_strength(pwm, pct):
    duty = int(pct * MAX_DUTY / 100)
    pwm.duty(duty)


def testElec():
    pwm = PWM(Pin(23), freq=50, duty=0)
    # Main loop
    while True:
        # Increase magnet strength gradually
        for duty_cycle in range(0, MAX_DUTY + 1, 10):
            set_magnet_strength(pwm, duty_cycle)
            time.sleep(0.1)  # Adjust delay as needed

        # Decrease magnet strength gradually
        for duty_cycle in range(MAX_DUTY, 0 - 1, -10):
            set_magnet_strength(pwm, duty_cycle)
            time.sleep(0.1)  # Adjust delay as needed

def start_pwm():
    pwm = PWM(Pin(23), freq=50, duty=0)
    set_magnet_strength(pwm, 50)


def main():
    start_pwm()


if __name__ == "__main__":
    main()