import sys
import numpy as np
from RPi_coms import setup_RPi_GPIO, move_motor_measure, do_cleanup


def move_sensor(dist_x: float = None, dist_y: float = None, dist_z: float = None, len_x: float = None, len_y : float = None, len_z : float = None) -> bool:
    # SETUP PINS for RPi
    GPIO_pin_config = dict(x_motor_dir=10, x_motor_step=8, y_motor_dir=18, y_motor_step=16, z1_motor_dir=13,
                           z1_motor_step=11, z2_motor_dir=31, z2_motor_step=29,
                           x_cal=50, y_cal=83, z_cal=83, sensor=37)  # all distance units in mm
    # RPi call
    setup_RPi_GPIO(GPIO_pin_config)

    delay = 0.001

    if np.abs(dist_x) > 0:
        _ = move_motor_measure(channel='x', dist=dist_x,
                               delay=delay, delay_measure=0,
                               GPIO_pin_config=GPIO_pin_config)
    if np.abs(dist_y) > 0:
        _ = move_motor_measure(channel='y', dist=dist_y,
                               delay=delay, delay_measure=0,
                               GPIO_pin_config=GPIO_pin_config)
    if np.abs(dist_z) > 0:
        _ = move_motor_measure(channel='z', dist=dist_z,
                               delay=delay, delay_measure=0,
                               GPIO_pin_config=GPIO_pin_config)


    max_y_allowed =  (len_y - np.abs(dist_y)) 
    max_z_allowed =  (len_z - np.abs(dist_z)) 
    max_x_allowed = len_x - np.abs(dist_x)
    return max_x_allowed, max_y_allowed, max_z_allowed


if __name__ == '__main__':
    # Seek inputs on the distance to move to home
    if len(sys.argv) < 4:
        print("Usage: move_to_home.py dist_x dist_y dist_z")
        print("Attention: Using defaults for 0.05T scanner measurements!")  #
        dist_x = 10  # mm
        dist_y = -10  # mm
        dist_z = 10  # mm
    elif len(sys.argv) == 4:
        dist_x = int(sys.argv[1])  # mm
        dist_y = int(sys.argv[2])  # mm
        dist_z = int(sys.argv[3])  # mm
    else:
        print("Error: Either use defaults or provide 4 inputs")
        print("Usage: measure_magnetic_field.py x_length y_length z_length resolution")
    print('This file assumes x: 390, y: 390, z:310 as the lengths') # This is the hardcoded limit switches implementation
    len_x = 390
    len_y = 390
    len_z = 310
    max_x_allowed, max_y_allowed, max_z_allowed = move_sensor(dist_x=dist_x, dist_y=dist_y, dist_z=dist_z, len_x=len_x, len_y=len_y, len_z = len_z)       #  z * 2;  y * 2
    print('Do NOT exceed -  x_len: ' + str(max_x_allowed) + 'mm y_len: ' + str(max_y_allowed) + 'mm z_len: ' + str(max_z_allowed) +  'mm')
    do_cleanup()
