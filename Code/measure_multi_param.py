import sys
import time
import numpy as np
from RPi_coms import setup_RPi_GPIO, move_motor_measure, do_cleanup  # RPi calls
from move_to_home import move_sensor
from Pi_16ADC import getreading


def get_locations(x_length: float = 265, y_length: float = 200, z_length: float = 200, resolution=10) -> np.ndarray:
    x = np.arange(0, x_length, resolution)
    # print("x array: " + str(x))

    y = np.arange(0, y_length, resolution)
    # print("y array: " + str(y))

    z = np.arange(0, z_length, resolution)
    # print("z array: " + str(z)) 

    return x, y, z


def move_and_measure(x: np.ndarray = None, y: np.ndarray = None, z: np.ndarray = None, resolution: float = None,
                     trajectory: str = 'Cartesian-EPI',
                     plot: bool = True, save_np_slice: bool = True, exp_num: int = 0) -> np.ndarray:
    # SETUP PINS for RPi
    GPIO_pin_config = dict(x_motor_dir=10, x_motor_step=8, y_motor_dir=18, y_motor_step=16, z1_motor_dir=13,
                           z1_motor_step=11, z2_motor_dir=31, z2_motor_step=29,
                           x_cal=50, y_cal=83, z_cal=83, 
                           address_adc=0b1110110, channel_0=0xB0, channel_1 = 0xB8,channel_2 = 0xB1,channel_3 = 0xB9,  
                           sensor_factor_mag=2053, sensor_factor_temp = 32, sensor_factor_temp_2 = -25.95)  # all distance units in mm

    # RPi call
    setup_RPi_GPIO(GPIO_pin_config)
    address_adc = GPIO_pin_config['address_adc'] # Making it more readable
    channel_0 = GPIO_pin_config['channel_0'] # Making it more readable
    channel_1 = GPIO_pin_config['channel_1'] # Making it more readable
    channel_2 = GPIO_pin_config['channel_2'] # Making it more readable
    channel_3 = GPIO_pin_config['channel_3'] # Making it more readable
    
    sensor_factor_mag = GPIO_pin_config['sensor_factor_mag'] # Making it more readable
    sensor_factor_temp = GPIO_pin_config['sensor_factor_temp'] # Making it more readable
    sensor_factor_temp_2 = GPIO_pin_config['sensor_factor_temp_2'] # Making it more readable

    delay_measure_acquire = 1 # Stabilize to make measurement
    delay = 0.0005 # 0.5 ms Speed of the motor - DO NOT CHANGE
    delay_motor_move = 0.1 * resolution #2 seconds to move 10 mm
    n_measurements = x.shape[0] * y.shape[0] * z.shape[0]
    print('Total measurements: ' + str(n_measurements))
    print('Estimated total time: ' + str((delay_measure_acquire + delay_motor_move) * n_measurements / 3600) + ' hours')
    field_map = np.zeros((n_measurements, 7), dtype=float)
    if trajectory == 'Cartesian_EPI':
        print("Starting measurements on Cartesian grid: x-slices for all y, z")
        print('Moving the sensor to top left corner of the grid')
        # ---------------
        # Move in z - UP
        # ----------------
        dist_z = (z[-1] + resolution) * 0.5
        print(dist_z)
        # RPi call
        _ = move_motor_measure(channel='z', dist=dist_z,
                               delay=delay, delay_measure=0,
                               GPIO_pin_config=GPIO_pin_config)

        # Move in y - LEFT
        dist_y = (-y[-1] - resolution) * 0.5
        print(dist_y)
        # RPi call
        _ = move_motor_measure(channel='y', dist=dist_y,
                               delay=delay, delay_measure=0,
                               GPIO_pin_config=GPIO_pin_config)

        # ---------------------------------
        # START measurements
        # ---------------------------------
        x_use = x
        y_use = y
        z_use = -1 * z  # To make the trajectory top down to start
        n = 0
        # sensor_value = np.zeros(1, dtype=float)
        y_ind = 0
        z_ind = 0
        for x_ind in range(x.shape[0]):
            dist_x = np.sign(x_use[x_ind]) * resolution
            print('Starting raster scanning now at x = ' + str(x[x_ind]))

            # RPi call
            _ = move_motor_measure(channel='x', dist=dist_x,
                                   delay=delay, delay_measure=0,
                                   GPIO_pin_config=GPIO_pin_config)  # CW is in to the bore

            for z_ind in range(z.shape[0]):
                dist_z = np.sign(z_use[z_ind]) * resolution

                # RPi call
                _ = move_motor_measure(channel='z', dist=dist_z,
                                       delay=delay, delay_measure=0,
                                       GPIO_pin_config=GPIO_pin_config)  # CW is in to the bore

                for y_ind in range(y.shape[0]):
                    dist_y = np.sign(y_use[y_ind]) * resolution
                    # print(x_use[x_ind], z_use[z_ind], y_use[y_ind]) # For debug
                    # print(x[x_ind], z[z_ind], y[y_ind]) # For debug

                    # RPi call
                    _ = move_motor_measure(channel='y', dist=dist_y,
                                                      delay=delay, delay_measure=0,
                                                      GPIO_pin_config=GPIO_pin_config)  # CW is in to the bore
                    time.sleep(delay_measure_acquire)
                    sensor_value_0 = sensor_factor_mag * getreading(address_adc, channel_0)
                    sensor_value_1 = (sensor_factor_temp * (2 * getreading(address_adc, channel_1)))  + sensor_factor_temp_2
                    sensor_value_2 = (sensor_factor_temp * (2 * getreading(address_adc, channel_2)))  + sensor_factor_temp_2
                    sensor_value_3 = (sensor_factor_temp * (2 * getreading(address_adc, channel_3)))  + sensor_factor_temp_2
                    print("Sensor_mag_value: " + str(sensor_value_0)+ " mT") 
                    print("Sensor_temp2_value: " + str(sensor_value_1)+ " C") 
                    print("Sensor_temp3_value: " + str(sensor_value_2)+ " C") 
                    print("Sensor_temp4_value: " + str(sensor_value_3)+ " C") 

                    # Store data
                    field_map[n, 0], field_map[n, 1], field_map[n, 2], field_map[n, 3], field_map[n, 4], field_map[n, 5], field_map[n, 6] = x_use[x_ind], z_use[z_ind], y_use[
                        y_ind], sensor_value_0, sensor_value_1, sensor_value_2, sensor_value_3
                    n += 1
                y_use = -1 * y_use  # Change direction to LEFT
            z_use = -1 * z_use  # Change direction to UP
            print('Completed raster scanning now at x = ' + str(x[x_ind]))

            

            if save_np_slice is True:  # Overwriting for now
                # fname = 'Slice_' + str(x[x_ind]) +'.npy'
                ctime = time.time()
                var = time.localtime(ctime)
                fname = 'Exp_' + str(exp_num) + '_' + str(var[0]) + str(var[1]) +  str(var[2]) + str(int(resolution))+ '.npy'
                print('Writing: ' + str(x[x_ind]) + ' slices to file: ', fname)
                np.save(fname, field_map)

        # Move back to home 
        home_x = -1 * x_use[-1]
        home_y = 0.5 * y_use[-1]
        home_z = 0.5 * z_use [-1]

        print("Returning to home!")
        print("home_x: " + str(home_x))
        print("home_y: " + str(home_y))
        print("home_z: " + str(home_z))
        move_sensor(dist_x= home_x, dist_y=home_y, dist_z=home_z)
    else:
        print("The rest of the trajectories are not done! Please choose Cartesian for now")
    return field_map


if __name__ == '__main__':
    # Seek inputs on the dimension of the cuboid TODO: incorporate sphere and cylinder
    if len(sys.argv) < 6:
        print("Usage: measure_multi_param.py x_length y_length z_length resolution")
        print("Attention: Using defaults for 0.05T scanner measurements!")  #
        x_length = 50  # mm
        y_length = 50  # mm
        z_length = 50  # mm
        resolution = 10  # mm
        exp_num = 0
    elif len(sys.argv) == 6:
        x_length = int(sys.argv[1])  # mm
        y_length = int(sys.argv[2])  # mm
        z_length = int(sys.argv[3])  # mm
        resolution = int(sys.argv[4])  # mm
        exp_num = int(sys.argv[5]) # arbitrary number
    else:
        print("Error: Either use defaults or provide 4 inputs")
        print("Usage: measure_multi_param.py x_length y_length z_length resolution experiment_number")

    # Get the locations to measure
    x, y, z = get_locations(x_length=x_length, y_length=y_length, z_length=z_length, resolution=resolution)

    # Traverse and measure at each location
    field_map = move_and_measure(x=x, y=y, z=z, resolution=resolution,
                                 trajectory='Cartesian_EPI',
                                 plot=True, save_np_slice=True, exp_num=exp_num)
    print(field_map.shape)
    do_cleanup()
