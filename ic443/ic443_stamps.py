import jjpy.cube as cube
import pyfits
import pywcs

import mpl_toolkits.axes_grid1 as axes_grid
from mpl_toolkits.axes_grid1 import anchored_artists

import matplotlib.pyplot as plt

def setup_axes(fig, imx_c, imy_c, cdelt_arcmin):
    from mpl_toolkits.axes_grid1.parasite_axes import HostAxes, ParasiteAxesAuxTrans

    grid = axes_grid.AxesGrid(fig, "111",
                              nrows_ncols=(4, 3), #ngrids=11,
                              direction='row', axes_pad=0.02,
                              add_all=True,
                              share_all=True, #False, share_x=False, share_y=False,
                              label_mode='1',
                              axes_class=(HostAxes, {}))

    from matplotlib.transforms import Affine2D
    for ax, imx, imy in zip(grid, imx_c, imy_c):
        aux_trans = Affine2D().translate(-imx, -imy).scale(cdelt_arcmin)
        ax2 = ParasiteAxesAuxTrans(ax, aux_trans,
                                   viewlim_mode="transform",
                                   )
        ax.parasites.append(ax2)
        ax.ax2 = ax2

    # colorbar axes
    from mpl_toolkits.axes_grid.inset_locator import inset_axes
    #import mpl_toolkits.axes_grid.axislines as axislines
    axins = inset_axes(grid[0],
                       width="5%",
                       height="50%",
                       loc=4,
                       )
                       #axes_class=axislines.Axes)

    #for d in ["right","bottom","top"]:
    axins.axis[:].toggle(all=False)
    axins.axis["left"].toggle(all=True)
    axins.axis["left"].label.set_size(10)

    return grid, axins


def determine_xy_peak_channel(cube, wcs):
    import pyfits
    data = pyfits.open("sc_fit.fits")[1].data
    ra_list = data.field("ra")
    dec_list = data.field("dec")

    imxs, imys = wcs.wcs_sky2pix(ra_list, dec_list, 0)

    peak_channel_list = []
    for x, y in zip(imxs, imys):
        s = cube.data[:,round(y),round(x)]
        peak_channel = s.argmax()
        peak_channel_list.append(peak_channel)

    return imxs, imys, peak_channel_list



if 1:

    c = pyfits.open("ic443_coN.raw.reorder.han-ind.contsub1.fits")
    wcs = pywcs.WCS(c[0].header).sub([1, 2])
    cube = cube.Cube(c[0].data, c[0].header)

    imx_c, imy_c, peak_channel_list = determine_xy_peak_channel(cube, wcs)
    cdelt_arcmin = abs(c[0].header["cdelt1"])*60.


    fig = plt.figure(1, figsize=(7., 10))

    grid, axins = setup_axes(fig, imx_c, imy_c, cdelt_arcmin)

    def get_translated_coord(i, x, y):
        return (x - imx_c[i])*cdelt_arcmin, (y - imy_c[i])*cdelt_arcmin

    mynorm=plt.Normalize()

    ny, nx = cube.data.shape[-2:]

    for i, ax in enumerate(grid):
        imx, imy, pc = imx_c[i], imy_c[i], peak_channel_list[i]
        chan = cube.channel(pc)
        x1, y1 = get_translated_coord(i, -0.5, -0.5, )
        x2, y2 = get_translated_coord(i, nx-0.5, ny-0.5)
        extent = x1, x2, y1, y2
        ax.imshow(chan.data, origin="lower",
                  interpolation="nearest",
                  cmap=plt.cm.gray_r,
                  norm=mynorm,
                  extent=extent)

        # with ax2, no need to modify the extent
        ax.ax2.contour(chan.data, [6, 8, 10],
                       colors="w")



    if 1: # mark maser
        """ VLA C-array :  12\arcsec
        06 17 29.3  +22 22 43
        06 18 03.7  +22 24 53
        """
        import coords
        p_list = [coords.Position("06:17:29.3  +22:22:43").j2000(),
                  coords.Position("06:18:03.7  +22:24:53").j2000(),
                  (94.181357,22.543208)]
        for p1, ax1 in zip(p_list, [grid[4], grid[5], grid[2]]):
            ra, dec = p1
            imx, imy = wcs.wcs_sky2pix([ra], [dec], 0)
            l1, = ax1.ax2.plot([imx], [imy],
                               "^", mec="k", mfc="w", mew=1, ms=8,
                               zorder=3.1)

        grid[-1].legend([l1], ["Maser"], loc=4, numpoints=1, handlelength=1,
                        prop=dict(size=10))

    dx, dy = 4, 4 # 4'
    grid.axes_llc.set_xlim(-dx, +dx)
    grid.axes_llc.set_ylim(-dy, +dy)

    mynorm.vmin=-0.3
    mynorm.vmax=5

    # add labels
    from itertools import count, izip
    try:
        from matplotlib.patheffects import withStroke
    except ImportError:
        withStroke = None

    for i, ax, pc in izip(count(1), grid, peak_channel_list):
        v = cube.ax.imz2skyz(pc)/1000.
        txt = anchored_artists.AnchoredText("SC %02d : $%4.1f$ km s$^{-1}$" % (i, v),
                                            loc=2,
                                            frameon=False,
                                            prop=dict(size=12))
        if withStroke:
            txt.txt._text.set_path_effects([withStroke(foreground="w",
                                                       linewidth=3)])
        ax.add_artist(txt)


    if 1: # colorbar
        cb = plt.colorbar(grid[0].images[0], cax = axins)
        cb.set_ticks([0, 2, 4])
        axins.axis["right"].toggle(all=False)
        axins.axis["left"].toggle(all=True)
        cb.set_label("T$^*$ [K]")


    grid.axes_llc.set_xlabel(r"$\Delta$ R.A. [$^{\prime}$]")
    grid.axes_llc.set_ylabel(r"$\Delta$ Dec. [$^{\prime}$]")

    grid.axes_llc.xaxis.get_major_locator()._nbins =  4
    grid.axes_llc.yaxis.get_major_locator()._nbins =  4

    # annotate plot SC 7
    a1 = grid[6].ax2.annotate("07", (imx_c[6], imy_c[6]),
                              xytext=(imx_c[6], imy_c[6]-12),
                              size=9, ha="center",
                              arrowprops=dict(arrowstyle="->",
                                              shrinkB=20,
                                              ))
    a1 = grid[6].ax2.annotate("08", (imx_c[7], imy_c[7]),
                              xytext=(imx_c[7], imy_c[7]-12),
                              size=9, ha="center",
                              arrowprops=dict(arrowstyle="->",
                                              shrinkB=20,
                                              ))

    # annotate plot 8
    a1 = grid[7].ax2.annotate("07", (imx_c[6], imy_c[6]),
                              xytext=(imx_c[6], imy_c[6]+12),
                              size=9, ha="center",
                              arrowprops=dict(arrowstyle="->",
                                              shrinkB=25,
                                              ))
    a1 = grid[7].ax2.annotate("08", (imx_c[7], imy_c[7]),
                              xytext=(imx_c[7], imy_c[7]-12),
                              size=9, ha="center",
                              arrowprops=dict(arrowstyle="->",
                                              shrinkB=20,
                                              ))


    plt.show()
