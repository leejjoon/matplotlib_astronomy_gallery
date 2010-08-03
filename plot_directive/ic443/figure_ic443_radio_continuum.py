import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import pyfits
import pywcsgrid2

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


def setup_axes():
    ax = pywcsgrid2.subplot(111, header=f_radio[0].header)

    # add colorbar axes
    divider = make_axes_locatable(ax)
    cax = divider.new_horizontal("5%", pad=0.1, axes_class=Axes)
    fig.add_axes(cax)

    return ax, cax

f_radio = pyfits.open("ic443.cont.clean_gull.immerge.nan.fits")

# Jy -> mJy
data = f_radio[0].data*1000

# prepare figure & axes
fig = plt.figure(1)
ax, cax = setup_axes()

# draw image
im = ax.imshow(data, cmap=plt.cm.gray_r, origin="lower", interpolation="nearest")
im.set_clim(0, 115)

# draw contour
cont = ax.contour(data, [20, 40, 60, 80, 100],
                  colors=["k","k","w", "w", "w"], alpha=0.5)
for col in cont.collections:
    col.set_linewidth(0.5)

cbar = plt.colorbar(im, cax=cax)

# adjust cbar ticks and and add levels for contour lines
cbar.set_ticks([0, 20, 40, 60, 80, 100])
cbar.add_lines(cont)

cax.set_ylabel("mJy/Beam")

ax.set(xlim=(75, 437), ylim=(65, 428))

ax.set_xlabel("Right Ascension (J2000)")
ax.set_ylabel("Declination (J2000)")

plt.show()

if 0:
    ax.set_rasterization_zorder(2.1)
    cax.set_rasterization_zorder(2.1)
    plt.savefig("a.eps", bbox_inches="tight", dpi=300)
