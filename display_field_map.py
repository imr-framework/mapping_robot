import matplotlib.pyplot as plt
from nibabel.viewers import OrthoSlicer3D
import numpy as np


def display_map(data: np.ndarray = None, display_type: str = 'scatter',
                n_x: int = None, n_y: int = None, n_z: int = None, resolution: int = None, order='xzy',
                flip_x_dim: bool = True,
                vmin: float = 0.04, vmax: float = 0.06) -> np.ndarray:
    image_data = np.zeros((n_x, n_y, n_z), dtype=float)

    if order == 'xzy':
        for n in range(data.shape[0]):
            x = int(np.squeeze(data[n, 0]) / resolution)
            y = int(np.squeeze(data[n, 1]) / resolution)
            z = int(np.squeeze(data[n, 2]) / resolution)
            sensor_value = np.squeeze(data[n, 3])
            image_data[x, z, y] = sensor_value
    print(data.shape)
    if flip_x_dim is True:
        for x_ind in range(n_x):
            if np.mod(x_ind, 2) != 0:
                sl = np.squeeze(image_data[x_ind, :, :])
                sl = np.fliplr(sl)
                sl = np.flipud(sl)
                image_data[x_ind, :, :] = sl

    if display_type == 'scatter':
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x_d = range(0, n_x, 1)
        y_d = range(0, n_y, 1)
        z_d = range(0, n_z, 1)
        x_m, y_m, z_m = np.meshgrid(x_d, y_d, z_d)
        scatter_data = image_data.flatten()

        img = ax.scatter(x_m * resolution, z_m * resolution, y_m * resolution, c=scatter_data, vmin=vmin, vmax=vmax, cmap=plt.jet())
        fig.colorbar(img)
        ax.view_init(elev=36, azim=114, roll=0)
        plt.show()
        display_data = 0

    if display_type == 'image':
        s = OrthoSlicer3D(image_data, affine=np.eye(4))
        s.cmap = 'jet'
        s.clim = [vmin, vmax]
        s.show()

    return sensor_value


if __name__ == '__main__':
    fname = './fmr/Exp_5_20231120.npy'
    data = np.load(fname)
    display_type = 'scatter'
    resolution = 4  # mm
    order = 'xzy'  # 100 x 100 x 100; # 300 x 170 x 170
    vmin = 0
    vmax = 200
    isotropic = True

    n_x = 20
    n_y = 20
    n_z = 20

    if isotropic:
        measurements = data.shape[0]
        print(measurements)
        n_x = int(np.cbrt(measurements))
        n_y = n_x
        n_z = n_x
        print(n_x, n_y, n_z)

    flip_x_dim = True   # because of the trajectory that moves zig zag in x-axis
    _ = display_map(data=data, display_type=display_type,
                    n_x=n_x, n_y=n_y, n_z=n_z, resolution=resolution, order=order, flip_x_dim=flip_x_dim,
                    vmin=vmin, vmax=vmax)
