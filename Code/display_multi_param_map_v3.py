import matplotlib.pyplot as plt
from nibabel.viewers import OrthoSlicer3D
import numpy as np
from measure_magnetic_field import get_locations
from scipy.signal import medfilt

def display_map(data: np.ndarray = None, display_type: str = 'scatter',
                n_x: int = None, n_y: int = None, n_z: int = None,
                resolution: int = None, order='xzy',
                cmap:str = None,
                vmin: np.ndarray = [40, 24], vmax: np.ndarray = [55, 28],
                longitudinal_single_point: bool = False,
                show_mag=False, plot_mag=False,
                show_temp = False, plot_temp = False, filter=True) -> np.ndarray:

    # Undo old voltage-temperature calibration :: m = 32, c = -25.95
    m = 32
    c = -25.95
    data[:, 4] = (data[:, 4] - c) / m
    data[:, 5] = (data[:, 5] - c) / m
    data[:, 6] = (data[:, 6] - c) / m

    # Calibrate the data for the temperature probes individually
    data[:, 4] = 27.219 * data[:, 4] - 19.5     # 20.11
    data[:, 5] = 24.713 * data[:, 5] - 15.844
    data[:, 6] = 33.571 * data[:, 6] - 30.174    # 31.174

    if longitudinal_single_point is True:
        image_data_mag = data[:, 3]
        image_data_temp1 = data[:, 4]
        image_data_temp2 = data[:, 5]
        image_data_temp3 = data[:, 6]
        
        if filter is True:
            image_data_mag = medfilt(image_data_mag, kernel_size=9)
            image_data_temp1 = medfilt(image_data_temp1, kernel_size=9)
            image_data_temp2 = medfilt(image_data_temp2, kernel_size=9)
            image_data_temp3 = medfilt(image_data_temp3, kernel_size=9)

        dt = 2           # Needs to be updated
        dt_min = 2 / 60
        T = dt * data.shape[0] / 60

        # fig = plt.figure()
        if plot_mag is True:
            plt.plot(np.arange(0, T, dt_min), image_data_mag)
            # plt.ylim(46, 49)
            plt.ylim(47, 48)
        if plot_temp is True:
            plt.plot(np.arange(0, T, dt_min), image_data_temp1, 'r')
            plt.plot(np.arange(0, T, dt_min), image_data_temp2, 'g')
            plt.plot(np.arange(0, T, dt_min), image_data_temp3, 'b')
            plt.legend(['Probe:1', 'Probe:2', 'Probe:3'])

        if show_mag is True:
            plt.grid()
            # plt.yticks(np.arange(46, 50, 1.0))
            plt.yticks(np.arange(47, 49, 0.5))
            plt.xticks(minor=False)
            plt.xlabel('Time (min.)', fontsize=18)
            plt.ylabel('Magnetic field (mT)', fontsize=18)
            plt.legend(['Trial 1', 'Trial2', 'Trial 3'])
            plt.show()
        if show_temp is True:
            plt.ylim(22, 25)
            plt.xlabel('Time (min.)', fontsize=18)
            plt.ylabel('Temperature ($^0 C$)', fontsize=18)
            plt.grid()
            plt.show()


    else:
        image_data_mag = np.zeros((n_x, n_y, n_z), dtype=float)
        image_data_temp1 = np.zeros((n_x, n_y, n_z), dtype=float)
        image_data_temp2 = np.zeros((n_x, n_y, n_z), dtype=float)
        image_data_temp3 = np.zeros((n_x, n_y, n_z), dtype=float)

        n = 0
        xa, ya, za = get_locations(x_length=n_x * resolution, z_length=n_z * resolution,
                                   y_length=n_z * resolution, resolution= resolution)
        x = np.int32(xa / resolution)
        y = np.int32(ya / resolution)
        z = np.int32(za / resolution)

        ndims = data.shape[1]
        if ndims > 4:
            multi_param = True
        else:
            multi_param = False

        if order == 'xzy':
            for x_ind in range(n_x):
                for z_ind in range(n_z):
                    for y_ind in range(n_y):
                        image_data_mag[x[x_ind], y[y_ind], z[z_ind]] = data[n, 3]
                        if multi_param is True:
                            image_data_temp1[x[x_ind], y[y_ind], z[z_ind]] = data[n, 4]
                            image_data_temp2[x[x_ind], y[y_ind], z[z_ind]] = data[n, 5]
                            image_data_temp3[x[x_ind], y[y_ind], z[z_ind]] = data[n, 6]
                        n += 1
                    y = np.flip(y)
                    # print(y)
                z = np.flip(z)
                # print(z)

        display_graph(display_type=display_type, data = image_data_mag, resolution=resolution,
                      vmin=vmin[0], vmax=vmax[0], cmap=cmap)

        if multi_param is True:

            display_graph(display_type=display_type, data = image_data_temp1, resolution=resolution,
                          vmin=vmin[1], vmax=vmax[1], cmap=cmap)

            display_graph(display_type=display_type, data=image_data_temp2, resolution=resolution,
                          vmin=vmin[1], vmax=vmax[1], cmap=cmap)

            display_graph(display_type=display_type, data=image_data_temp3, resolution=resolution,
                          vmin=vmin[1], vmax=vmax[1], cmap=cmap)

    return image_data_mag, image_data_temp1, image_data_temp2, image_data_temp3

def display_graph(display_type:str=None, data:np.ndarray=None, resolution:int=None,
                  vmin:int = None, vmax:int = None, cmap:str=None):
        n_x, n_y, n_z = data.shape

        if display_type == 'scatter':
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            x_d = range(0, n_x, 1)
            y_d = range(0, n_y, 1)
            z_d = range(0, n_z, 1)
            x_m, y_m, z_m = np.meshgrid(x_d, z_d, y_d)
            # Meshgrid is messed - produces different axis than expected
            x_m = np.moveaxis(x_m, [0, 1, 2], [1, 0, 2])
            y_m = np.moveaxis(y_m, [0, 1, 2], [1, 0, 2])
            z_m = np.moveaxis(z_m, [0, 1, 2], [1, 0, 2])
            scatter_data = data.flatten()
            if cmap == 'hot':
                img = ax.scatter(x_m * resolution, z_m * resolution, y_m * resolution, c=scatter_data, vmin=vmin, vmax=vmax, cmap=plt.hot())
            else:
                img = ax.scatter(x_m * resolution, z_m * resolution, y_m * resolution, c=scatter_data, vmin=vmin,
                                 vmax=vmax, cmap=plt.jet())

            fig.colorbar(img)
            ax.view_init(elev=36, azim=114, roll=0)
            plt.show()

        if display_type == 'image':
            s = OrthoSlicer3D(data, affine=np.eye(4))
            s.cmap = cmap
            s.clim = [vmin, vmax]
            s.show()

if __name__ == '__main__':
    # fname = './fmr_data/multi_parameter/Exp_2_202312210.npy'
    # fname = './fmr_data/Temperature_Magnetic_field_time/Exp_6_202312610.npy'

    # Motor on
    # fname = './fmr_data/multi_parameter/Exp_2_202312210.npy'
    # fname = './fmr_data/multi_parameter/Exp_3_202312310.npy'

    # Motor off
    fname1 = './fmr_data/Temperature_Magnetic_field_time/Exp_4_202312410.npy'
    fname2 = './fmr_data/Temperature_Magnetic_field_time/Exp_5_202312510.npy'
    fname3 = './fmr_data/Temperature_Magnetic_field_time/Exp_6_202312610.npy'
    filtering = True
   

    data1 = np.load(fname1)
    data2 = np.load(fname2)
    data3 = np.load(fname3)
    
     # Filtering to address reviewer comments
    # if filtering is True:
    #     data1 = np.median(data1, axis=0)
    #     data2 = np.median(data2, axis=0)
    #     data3 = np.median(data3, axis=0)
    
    display_type = 'scatter'
    resolution = 10  # mm
    order = 'xzy'  # 100 x 100 x 100; # 300 x 170 x 170
    vmin = [40, 22]  # 40
    vmax = [55, 25]  # 55
    isotropic = False
    longitudinal_single_point = True


    n_x = 30
    n_y = 16
    n_z = 16

    if isotropic:
        measurements = data1.shape[0]
        print(measurements)
        n_x = int(np.cbrt(measurements))
        n_y = n_x
        n_z = n_x
        print(n_x, n_y, n_z)


    _ = display_map(data=data1, display_type=display_type,
                    n_x=n_x, n_y=n_y, n_z=n_z, resolution=resolution, order=order,
                    vmin=vmin, vmax=vmax, cmap='jet',
                    longitudinal_single_point=longitudinal_single_point,
                    show_temp=False, plot_mag=True, plot_temp=False)
    _ = display_map(data=data2, display_type=display_type,
                    n_x=n_x, n_y=n_y, n_z=n_z, resolution=resolution, order=order,
                    vmin=vmin, vmax=vmax, cmap='jet',
                    longitudinal_single_point=longitudinal_single_point,
                    show_temp=False,plot_mag=True, plot_temp=False)
    _ = display_map(data=data3, display_type=display_type,
                    n_x=n_x, n_y=n_y, n_z=n_z, resolution=resolution, order=order,
                    vmin=vmin, vmax=vmax, cmap='jet',
                    longitudinal_single_point=longitudinal_single_point,
                    show_mag=True,plot_mag=True, plot_temp=False)

