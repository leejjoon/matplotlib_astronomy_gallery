import pyfits
import pywcsgrid2
import matplotlib.pyplot as plt
import matplotlib

colormap = matplotlib.cm.gist_heat_r

def setup_axes(fig, rect, zoom=0.35, loc=4, axes_class=None, axes_kwargs=None):
    """
    ax2 is an inset axes, but shares the x- and y-axis with ax1.
    """

    from pywcsgrid2.axes_grid.axes_grid import ImageGrid

    grid = ImageGrid(fig, rect,
                     nrows_ncols=(1,2),
                     share_all=True, aspect=True,
                     label_mode='L', cbar_mode="each",
                     cbar_location='top', cbar_pad=None, cbar_size='5%',
                     axes_class=(axes_class, axes_kwargs))

    return grid[0], grid[1]


def set_axes2(ax1, axes_class, axes_kwargs):

    import pywcsgrid2.axes_grid.inset_locator as inset_locator

    ax3 = inset_locator.zoomed_inset_axes(ax1, zoom=4, loc=1,
                                          bbox_to_anchor=None,
                                          bbox_transform=None,
                                          axes_class=axes_class,
                                          axes_kwargs=axes_kwargs,
                                          )

    ax3.axis[:].toggle(all=False)

    return ax3


if 1:

    f_kpno = pyfits.open("tycho_kpno_2007_knotg.fits")
    f_hst = pyfits.open("tycho_5_drz_sci2_knotg.fits")

    fig = plt.figure(1, figsize=(7, 5))

    gh = pywcsgrid2.GridHelper(wcs=f_hst[0].header)
    axes_kwargs = dict(grid_helper=gh)

    ax1, ax2 = setup_axes(fig, rect=111,
                          zoom=0.35, loc=4,
                          axes_class=pywcsgrid2.Axes, axes_kwargs=axes_kwargs)

    # draw data


    from scipy.ndimage import gaussian_filter
    d_hst = gaussian_filter(f_hst[0].data.astype("d"), 1.5)
    im_hst = ax1.imshow(d_hst,
                        origin="lower",
                        interpolation="nearest",
                        cmap=colormap)

    im_hst.set_clim(0.0022, 0.0087)
    ax1.cax.colorbar(im_hst)
    ax1.cax.axis["top"].toggle(all=True)
    ax1.cax.set_xlabel(r"H$\alpha$ Intensity")

    ax1.set_xlim(118.5, 1130.5)
    ax1.set_ylim(47.5, 1422.5)



    im_kpno = ax2[f_kpno[0].header].imshow(f_kpno[0].data,
                                           origin="lower", cmap=colormap,
                                           interpolation="nearest",
                                           oversample=1.)
    im_kpno.set_clim(39, 90)
    ax2.cax.colorbar(im_kpno)
    ax2.cax.axis["top"].toggle(all=True)
    ax2.cax.set_xlabel(r"H$\alpha$ Intensity")



    # add an inset

    gh3 = pywcsgrid2.GridHelper(wcs=f_hst[0].header)
    ax3 = set_axes2(ax1,
                    axes_class=pywcsgrid2.Axes,
                    axes_kwargs=dict(grid_helper=gh3))
    im_hst2 = ax3.imshow(d_hst,
                         origin="lower",
                         interpolation="nearest",
                         cmap=colormap)
    im_hst2.set_clim(0.0028, 0.0187)
    ax3.set(xlim=(592,656+10),
            ylim=(803,890))

    # adjust the location
    from pywcsgrid2.axes_grid.inset_locator import mark_inset
    ax3.get_axes_locator().loc = 4
    p = mark_inset(ax1, ax3, loc1=1, loc2=3, alpha=0.5)
    p[0].set(fc="none")

    ax3.add_size_bar(1/3600./f_hst[0].header["cdelt2"],
                     r"$1^{\prime\prime}$", loc=3,
                     borderpad=0.2)


    from matplotlib.patheffects import withStroke

    t1 = ax1.add_inner_title("(a) HST", 2, frameon=False)
    t1.txt._text.set_path_effects([withStroke(linewidth=3, foreground="w")])

    t2 = ax2.add_inner_title("(b) KPNO", 2, frameon=False)
    t2.txt._text.set_path_effects([withStroke(linewidth=3, foreground="w")])


    plt.show()

