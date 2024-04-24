import time
from machine import Pin
from Robot import Robot


def cycleCards(num=1, press_dur=1500, retract_dur=2000):
	rob = Robot()
	rob.arm.set_position_with_speed((0, 130, 200), 0.3)
	for cycle in range(num):
		for i in range(3):
			rob.end_effector.set_card(i)
			time.sleep_ms(500)
			rob.arm.set_position_with_speed((0, 230, 190), 0.3)
			time.sleep_ms(press_dur)
			rob.arm.set_position_with_speed((0, 130, 200), 0.3)
			time.sleep_ms(retract_dur)
		rob.arm.teaching_mode()


def checkColor():
	rob = Robot()
	rgb_sensor = rob.RGB_sensor
	led_seg_disp = rob.LED_seg_disp

	while True:
	
		r, g, b = rgb_sensor.readRGBLight()

		if r > 25 and r > g and r > b:
			led_seg_disp.tube_display("red")
		elif g > 25 and g > r and g > b:
			led_seg_disp.tube_display("grn")
		elif b > 80 and b > g and b > r:
			led_seg_disp.tube_display("blue")
		else:
			led_seg_disp.tube_display("none")
		# time.sleep_ms(25)
		
		print(str(r) + ", " + str(g) + ", " + str(b))


def cycle7SegDisp():
	rob = Robot()
 
	led_seg_disp = rob.LED_seg_disp
 
	led_seg_disp.update_display()
	led_seg_disp.brightness(5)
 
	for i in range(10000, 11000):
		led_seg_disp.tube_display(i, overFlowText=False)


def moveArm():
	rob = Robot()
	arm = rob.arm
	# positions = [(196, -52, 203), (140, -221, 121), (-1, -200, 188), (-124, -220, 113), (-167, -79, 153), (-256, -79, 83), (216, -151, 89), (264, 8, 89), (-138, -233, 75), (0, -193, 68)]
	positions = [(0, -200, 200), (0, -125, 200), (0, -200, 200), (0, -200, 200), (0, -200, 100)]

	for i, pos in enumerate(positions):
		rob.LED_seg_disp.tube_display(i+1)
		arm.set_position(pos, 1000)
		time.sleep_ms(2000)
		
	arm.go_home()
	rob.LED_seg_disp.tube_display_flash(len(positions), num_flash=3, flash_speed=750)
	rob.LED_seg_disp.update_display()
	time.sleep_ms(2000)
	arm.teaching_mode()


def learnArmPos():
	rob = Robot()
	positions = []
	button = Pin(0)
	rob.LED_seg_disp.tube_display(len(positions))
	rob.arm.teaching_mode()

	def learnCurPos(pin):
		curPos = rob.arm.read_position()
		positions.append(curPos)
		print(str(len(positions)) + ": " + str(curPos))
		rob.LED_seg_disp.tube_display(len(positions))

	button.irq(handler=learnCurPos, trigger=Pin.IRQ_FALLING)

	input("Move arm to position. Press button to record position. When finished, press enter.\n")

	print(positions)
	rob.LED_seg_disp.tube_display_flash(len(positions), num_flash=3, flash_speed=750)
	rob.LED_seg_disp.update_display()


def main():
	cycleCards()
 

if __name__ == '__main__':
	main()
