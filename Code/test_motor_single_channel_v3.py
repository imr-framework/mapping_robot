import RPi.GPIO as GPIO
from time import sleep

def setup_RPi_GPIO(GPIO_pin_config: dict = None) -> bool:
    # Setup pin layout on PI
    GPIO.setmode(GPIO.BOARD)

    # Establish Pins in software
    GPIO.setup(GPIO_pin_config['x_motor_dir'], GPIO.OUT)
    GPIO.setup(GPIO_pin_config['x_motor_step'], GPIO.OUT)

    GPIO.setup(GPIO_pin_config['y_motor_dir'], GPIO.OUT)
    GPIO.setup(GPIO_pin_config['y_motor_step'], GPIO.OUT)

    GPIO.setup(GPIO_pin_config['z1_motor_dir'], GPIO.OUT)
    GPIO.setup(GPIO_pin_config['z1_motor_step'], GPIO.OUT)

    GPIO.setup(GPIO_pin_config['z2_motor_dir'], GPIO.OUT)
    GPIO.setup(GPIO_pin_config['z2_motor_step'], GPIO.OUT)

    return True


def move_motor(channel: str = 'x', dir: str = 'CW', steps: int = 200, delay=0.02, GPIO_pin_config: dict = None) -> bool:
    CW = 1
    CCW = 0
    try:
        if channel == 'x':
            if dir == 'CW':
                GPIO.output(GPIO_pin_config['x_motor_dir'], CW)
            elif dir == 'CCW':
                GPIO.output(GPIO_pin_config['x_motor_dir'], CW)
            sleep(delay)
            for step in range(steps):
                GPIO.output(GPIO_pin_config['x_motor_step'], GPIO.HIGH)
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output(GPIO_pin_config['x_motor_step'], GPIO.LOW)
                sleep(delay)  # Dictates how fast stepper motor will run

        if channel == 'y':
            if dir == 'CW':
                GPIO.output(GPIO_pin_config['y_motor_dir'], CW)
            elif dir == 'CCW':
                GPIO.output(GPIO_pin_config['y_motor_dir'], CW)
            sleep(delay)
            for step in range(steps):
                GPIO.output(GPIO_pin_config['y_motor_step'], GPIO.HIGH)
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output(GPIO_pin_config['y_motor_step'], GPIO.LOW)
                sleep(delay)  # Dictates how fast stepper motor will run

        if channel == 'z':
            if dir == 'CW':
                GPIO.output((GPIO_pin_config['z1_motor_dir'], GPIO_pin_config['z2_motor_dir']), (CW, CW))
            elif dir == 'CCW':
                GPIO.output((GPIO_pin_config['z1_motor_dir'], GPIO_pin_config['z2_motor_dir']), (CCW,CCW))
            sleep(delay)
            for step in range(steps):
                GPIO.output((GPIO_pin_config['z1_motor_step'], GPIO_pin_config['z2_motor_step']),
                            (GPIO.HIGH, GPIO.HIGH))
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output((GPIO_pin_config['z1_motor_step'], GPIO_pin_config['z2_motor_step']),
                            (GPIO.LOW, GPIO.LOW))
                sleep(delay)  # Dictates how fast stepper motor will run
    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        GPIO.cleanup()
    return True


if __name__ == '__main__':
    # SETUP PINS for RPi
    GPIO_pin_config = dict(x_motor_dir=10, x_motor_step=8, y_motor_dir=18, y_motor_step=16, z1_motor_dir=13,
                           z1_motor_step=11, z2_motor_dir=31, z2_motor_step=29)

    setup_RPi_GPIO(GPIO_pin_config)

    # Do items on one channel
    channel = 'z'
    dir = 'CCW'
    steps = 417
    delay = 0.001
    move_motor(channel=channel, dir=dir, steps=steps,delay = delay, GPIO_pin_config=GPIO_pin_config)
    print("Done moving: cleaning up")
    GPIO.cleanup()
