import pyfits
import numpy as np
import matplotlib.pyplot as plt

import pywcsgrid2
try:
    from pywcsgrid2.axes_grid.axes_rgb import imshow_rgb
except ImportError:
    from mpl_toolkits.axes_grid.axes_rgb import imshow_rgb


# prepare dara

f = pyfits.open("ic443_co.ambient.fits")
import jjpy.cube as cube
c = cube.Cube(f[0].data, f[0].header)
r = c.squash(-0.5e3, -3.4e3, coord="sky", mode="sum")
g = c.squash(-3.4e3, -5.1e3, coord="sky", mode="sum")
b = c.squash(-5.1e3, -7e3, coord="sky", mode="sum")

f_radio = pyfits.open("ic443.cont.clean_gull.immerge.nan.fits")
data = f_radio[0].data*1000
    
def mytrim(d, vmin, vmax):
    dd = (d + vmin) /(vmin + vmax)
    return np.clip(dd, 0, 1)


# draw figure

ax = pywcsgrid2.subplot(111, header=f[0].header)
i = imshow_rgb(ax,
               mytrim(r.data, 0, 7),
               mytrim(g.data, 0, 7),
               mytrim(b.data, 0, 7),
               origin="lower", interpolation="nearest",
               )

ax.axis[:].major_ticks.set_color("w")

    
cont = ax[f_radio[0].header].contour(data, [10, 20, 40, 60, 80],
                                     colors="w", alpha=0.5)

plt.show()
