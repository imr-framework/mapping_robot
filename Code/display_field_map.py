import matplotlib.pyplot as plt
from nibabel.viewers import OrthoSlicer3D
import numpy as np


def display_map(data: np.ndarray = None, display_type: str = 'scatter',
                n_x:int=None, n_y:int=None, n_z:int=None, resolution: int = None, order='xzy',
                vmin: float = 0.04, vmax: float = 0.06) -> np.ndarray:
    if display_type == 'scatter':
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x = np.squeeze(data[:, 0])
        z = np.squeeze(data[:, 1])
        y = np.squeeze(data[:, 2])
        sensor_value = np.squeeze(data[:, 3])

        img = ax.scatter(x, z, y, c=sensor_value, vmin=vmin, vmax=vmax, cmap=plt.hot())
        fig.colorbar(img)
        plt.show()
        display_data = 0

    if display_type == 'image':
        image_data = np.zeros((n_x, n_y, n_z), dtype=float)
        if order == 'xzy':
            for n in range(data.shape[0]):
                x = int(np.squeeze(data[n, 0]) / resolution)
                y = int(np.squeeze(data[n, 1]) / resolution)
                z = int(np.squeeze(data[n, 2]) / resolution)
                sensor_value = np.squeeze(data[n, 3])
                image_data[x, z, y] = sensor_value
                display_data = image_data
        s = OrthoSlicer3D(image_data, affine=np.eye(4))
        s.cmap = 'hot'
        s.clim = [vmin, vmax]
        s.show()


    return display_data


if __name__ == '__main__':
    data = np.load('Slice_by_slice.npy')
    display_type = 'scatter'
    resolution = 1 # mm
    order = 'xzy'
    vmin = 0.04
    vmax = 0.06
    n_x = 50
    n_y = 50
    n_z = 50
    _ = display_map(data=data, display_type=display_type,
                    n_x=n_x, n_y=n_y, n_z=n_z, resolution=resolution, order=order,
                    vmin=vmin, vmax=vmax)
