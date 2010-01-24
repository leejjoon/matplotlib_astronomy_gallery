import pywcsgrid2
import pyfits
import pywcsgrid2.axes_grid.axislines as axislines
import matplotlib.pyplot as plt

class Velo(object):
    def __init__(self, header):
        self.crpix = header["CRPIX3"]
        self.crval = header["CRVAL3"]
        self.cdelt = header["CDELT3"]

    def to_pixel(self, v):
        return (v - self.crval)/self.cdelt + self.crpix - 1

    def to_vel(self, p):
        return (p + 1 - self.crpix)*self.cdelt + self.crval


def setup_axes(fig, header):
    from mpl_toolkits.axes_grid import make_axes_locatable

    ax0 = pywcsgrid2.subplot(111, wcs=header)
    divider = make_axes_locatable(ax0)

    ax_v = divider.new_vertical(1.5, pad=0.1, sharex=ax0,
                                axes_class=axislines.Axes)
    fig.add_axes(ax_v)

    ax_h = divider.new_horizontal(1.5, pad=0.1, sharey=ax0,
                                  axes_class=axislines.Axes)

    fig.add_axes(ax_h)


    new_axis = ax0.get_grid_helper().new_fixed_axis
    ax_h.axis["left"] = new_axis("left", axes=ax_h)
    ax_h.axis["right"] = new_axis("right", axes=ax_h)
    ax_h.axis["left"].toggle(ticklabels=False)
    ax_h.axis["right"].toggle(ticklabels=False)

    ax_v.axis["top"] = new_axis("top", axes=ax_v)
    ax_v.axis["bottom"] = new_axis("bottom", axes=ax_v)
    ax_v.axis["top"].toggle(ticklabels=False)
    ax_v.axis["bottom"].toggle(ticklabels=False)


    return ax0, ax_v, ax_h


fits_cube = pyfits.open("ic443_co.ambient.fits")
header = fits_cube[0].header

vel = Velo(header)


import matplotlib.colors as mcolors
norm = mcolors.Normalize()
cmap = plt.cm.gray_r

fits_cube[0].data = fits_cube[0].data**2

vv0  = fits_cube[0].data.max(axis=0) #.sum(axis=1)
vv1  = fits_cube[0].data.max(axis=1)
vv2  = fits_cube[0].data.max(axis=2).transpose()


fig = plt.figure(1, figsize=(6, 6))
ax0, ax_v, ax_h = setup_axes(fig, header)

im0 = ax0.imshow(vv0, origin="lower", interpolation="nearest",
                 norm=norm, cmap=cmap)

ax_v.imshow(vv1, origin="lower", aspect="auto",
            interpolation="nearest", norm=norm, cmap=cmap)


ax_h.imshow(vv2, origin="lower", aspect="auto",
            interpolation="nearest", norm=norm,
            cmap=cmap)

ax_h.axis["bottom"].label.set_text(r"$v_{\mathrm{LSR}}$ [km s$^{-1}$]")
ax_v.axis["left"].label.set_text(r"$v_{\mathrm{LSR}}$ [km s$^{-1}$]")


norm.vmin=0.1
norm.vmax=5**2
for ax in [ax0, ax_h, ax_v]:
    ax.images[0].changed()

v = [-10, -5, 0, -5]
vl = [("$%d$" % v1) for v1 in v]
vp = [vel.to_pixel(v1*1000.) for v1 in v]
ax_h.set_xticks(vp)
ax_h.set_xticklabels(vl)
ax_v.set_yticks(vp)
ax_v.set_yticklabels(vl)


# draw grid
gh = ax0.get_grid_helper()
gh.update_lim(ax0)

for t in gh.get_tick_iterator(0, "bottom"):
    ax0.axvline(t[0][0], color="0.5", ls=":")
    ax_v.axvline(t[0][0], color="0.5", ls=":")
for t in gh.get_tick_iterator(1, "left"):
    ax0.axhline(t[0][1], color="0.5", ls=":")
    ax_h.axhline(t[0][1], color="0.5", ls=":")


plt.show()

