import RPi.GPIO as GPIO
from time import sleep
import numpy as np


def setup_RPi_GPIO(GPIO_pin_config: dict = None) -> bool:
    print("Setting up RPi pins")
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

    # GPIO.setup(GPIO_pin_config['sensor'], GPIO.IN)
    return True


def move_motor_measure(channel: str = 'x',dist: float = 10,
                       delay=0.02, delay_measure=2,
                       GPIO_pin_config: dict = None) -> float:
    CW = 1
    CCW = 0
    try:
        if channel == 'x':
            if dist >= 0:  # IN to the bore
                dir_x = CW
            else:
                dir_x = CCW  # OUT of the bore

            GPIO.output(GPIO_pin_config['x_motor_dir'], dir_x)
            sleep(delay)
            x_steps = int(np.abs(dist) * GPIO_pin_config['x_cal'])
            # print(x_steps)
            for x_step in range(x_steps):
                GPIO.output(GPIO_pin_config['x_motor_step'], GPIO.HIGH)
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output(GPIO_pin_config['x_motor_step'], GPIO.LOW)
                sleep(delay)  # Dictates how fast stepper motor will run

        if channel == 'y':
            if dist >= 0:  # RIGHT of the center - can also use sign to check if faster
                dir_y = CW
            else:
                dir_y = CCW  # LEFT of the center
            GPIO.output(GPIO_pin_config['y_motor_dir'], dir_y)
            sleep(delay)

            y_steps = int(np.abs(dist) * GPIO_pin_config['y_cal'])
            for y_step in range(y_steps):
                GPIO.output(GPIO_pin_config['y_motor_step'], GPIO.HIGH)
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output(GPIO_pin_config['y_motor_step'], GPIO.LOW)
                sleep(delay)  # Dictates how fast stepper motor will run

        if channel == 'z':
            if dist >= 0:  # UP direction
                dir_z = CCW
            else:
                dir_z = CW  # DOWN direction
            # if dir == CW:
            GPIO.output((GPIO_pin_config['z1_motor_dir'], GPIO_pin_config['z2_motor_dir']), (dir_z, dir_z))
            # elif dir == 'CCW':
            #     GPIO.output((GPIO_pin_config['z1_motor_dir'], GPIO_pin_config['z2_motor_dir']), (CW, CW))
            sleep(delay)
            z_steps = int(np.abs(dist) * GPIO_pin_config['z_cal'])
            for z_step in range(z_steps):
                GPIO.output((GPIO_pin_config['z1_motor_step'], GPIO_pin_config['z2_motor_step']),
                            (GPIO.HIGH, GPIO.HIGH))
                # Allow it to get there.
                sleep(delay)  # Dictates how fast stepper motor will run
                # Set coil winding to low
                GPIO.output((GPIO_pin_config['z1_motor_step'], GPIO_pin_config['z2_motor_step']),
                            (GPIO.LOW, GPIO.LOW))
                sleep(delay)  # Dictates how fast stepper motor will run
        if delay_measure > 0:  # Do measurement
            sleep(delay_measure)
            sensor_value = GPIO.input(GPIO_pin_config['sensor'])
            print(GPIO_pin_config['sensor'])
        else:
            sensor_value = np.NaN


    # Once finished clean everything up
    except KeyboardInterrupt:
        sensor_value = np.NaN
        print("cleanup")
        GPIO.cleanup()

    return sensor_value

def do_cleanup():
    print("Cleaning up")
    GPIO.cleanup()


if __name__ == '__main__':
    # SETUP PINS for RPi
    GPIO_pin_config = dict(x_motor_dir=10, x_motor_step=8, y_motor_dir=18, y_motor_step=16, z1_motor_dir=13,
                           z1_motor_step=11, z2_motor_dir=31, z2_motor_step=29,
                           x_cal=50, y_cal=83, z_cal=83, 
                           address_adc=0b1110110, channel_0=0xB0, channel_1 = 0xB8,channel_2 = 0xB1,channel__3 = 0xB9,  
                           sensor_factor_mag=2053)  # all distance units in mm

    setup_RPi_GPIO(GPIO_pin_config)

    # Do items on one channel
    channel = 'y'
    dir = 'CW'
    dist = 10 # mm
    delay = 0.001
    delay_measure = 2
    sensor_value = move_motor_measure(channel=channel, dist=dist,
                                      delay=delay, delay_measure=delay_measure,
                                      GPIO_pin_config=GPIO_pin_config)
    print("Done moving: cleaning up")
    GPIO.cleanup()
