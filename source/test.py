import time
from espmax import ESPMax
from RobotControl import RobotControl
from TM1640 import TM1640
from Color_sensor import COLOR
from machine import Pin, I2C
from micropython import const


def checkColor():
	i2c = I2C(0, scl=Pin(16), sda=Pin(17), freq=100000)
	apds = COLOR(i2c)
	apds.enableLightSensor(True)

	tm = TM1640(clk=Pin(33), dio=Pin(32))

	while True:
	
		r, g, b = apds.readRGBLight()

		if r > 25 and r > g and r > b:
			tm.tube_display("red")
		elif g > 25 and g > r and g > b:
			tm.tube_display("grn")
		elif b > 80 and b > g and b > r:
			tm.tube_display("blue")
		else:
			tm.tube_display("none")
		# time.sleep_ms(25)
		
		print(str(r) + ", " + str(g) + ", " + str(b))


def cycle7SegDisp():
	tm = TM1640(clk=Pin(33), dio=Pin(32))
	tm.update_display()
	tm.brightness(5)
	for i in range(10000, 11000):
		tm.tube_display(i, overFlowText=False)


def moveArm():
	rob = RobotControl()
	arm = rob.arm
	positions = [(196, -52, 203), (140, -221, 121), (-1, -200, 188), (-124, -220, 113), (-167, -79, 153), (-256, -79, 83), (216, -151, 89), (264, 8, 89), (-138, -233, 75), (0, -193, 68)]

	tm = TM1640(clk=Pin(33), dio=Pin(32))

	for i, pos in enumerate(positions):
		tm.tube_display(i+1)
		arm.set_position(pos, 1000)
		time.sleep_ms(2000)
		
	arm.go_home()
	tm.tube_display_flash(len(positions), num_flash=3, flash_speed=750)
	tm.update_display()
	time.sleep_ms(2000)
	arm.teaching_mode()


def learnArmPos():
	rob = RobotControl()
	positions = []
	button = Pin(0)
	tm = TM1640(clk=Pin(33), dio=Pin(32))
	tm.tube_display(len(positions))
	rob.arm.teaching_mode()

	def learnCurPos(pin):
		curPos = rob.arm.read_position()
		positions.append(curPos)
		print(str(len(positions)) + ": " + str(curPos))
		tm.tube_display(len(positions))

	button.irq(handler=learnCurPos, trigger=Pin.IRQ_FALLING)

	input("Move arm to position. Press button to record position. When finished, press enter.\n")

	print(positions)
	tm.tube_display_flash(len(positions), num_flash=3, flash_speed=750)
	tm.update_display()


def main():
	# checkColor()
	cycle7SegDisp()
	# moveArm()
	# learnArmPos()
	pass


if __name__ == '__main__':
	main()
