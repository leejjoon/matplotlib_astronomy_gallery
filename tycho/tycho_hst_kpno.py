import pyfits
import pywcsgrid2
import matplotlib.pyplot as plt
import matplotlib
import mpl_toolkits.axisartist as axisartist

colormap = matplotlib.cm.gist_heat_r

def setup_axes01(fig, rect, axes_class=None, axes_kwargs=None):
    """
    ax2 is an inset axes, but shares the x- and y-axis with ax1.
    """

    from mpl_toolkits.axes_grid1.axes_grid import ImageGrid

    grid = ImageGrid(fig, rect,
                     nrows_ncols=(1,2),
                     share_all=True, aspect=True,
                     label_mode='L', cbar_mode="each",
                     cbar_location='top', cbar_pad=None, cbar_size='5%',
                     axes_class=(axes_class, axes_kwargs))

    return grid[0], grid[1]


def setup_axes02(fig, rect, zoom=0.35, loc=4, axes_class=None, axes_kwargs=None):
    """
    ax2 is an inset axes, but shares the x- and y-axis with ax1.
    """

    from mpl_toolkits.axes_grid1.axes_grid import ImageGrid, CbarAxes
    import mpl_toolkits.axes_grid1.inset_locator as inset_locator

    grid = ImageGrid(fig, rect,
                     nrows_ncols=(1,1),
                     share_all=True, aspect=True,
                     label_mode='L', cbar_mode="each",
                     cbar_location='top', cbar_pad=None, cbar_size='5%',
                     axes_class=(axes_class, axes_kwargs))

    ax1 = grid[0]
    
    kwargs = dict(zoom=zoom, loc=loc)
    ax2 = inset_locator.zoomed_inset_axes(ax1, 
                                          axes_class=axes_class,
                                          axes_kwargs=axes_kwargs,
                                          **kwargs
                                          )

    
    cax = inset_locator.inset_axes(ax2, "100%", 0.05, loc=3,
                                   borderpad=0.,
                                   bbox_to_anchor=(0, 0, 1, 0),
                                   bbox_transform=ax2.transAxes,
                                   axes_class=CbarAxes,
                                   axes_kwargs=dict(orientation="top"),
                                   )

    ax2.cax = cax
    return grid[0], ax2


def setup_inset_axes(parent_axes, f_hst, **kwargs):
    import mpl_toolkits.axes_grid1.inset_locator as inset_locator

    if "zoom" not in kwargs:
        kwargs["zoom"] = 4
    if "loc" not in kwargs:
        kwargs["loc"] = 1

    gh3 = pywcsgrid2.GridHelper(wcs=f_hst[0].header)

    axes_class = pywcsgrid2.Axes
    axes_kwargs=dict(grid_helper=gh3)
    
    ax3 = inset_locator.zoomed_inset_axes(parent_axes, 
                                          #bbox_to_anchor=None,
                                          #bbox_transform=None,
                                          axes_class=axes_class,
                                          axes_kwargs=axes_kwargs,
                                          **kwargs
                                          )

    ax3.axis[:].toggle(all=False)

    return ax3


def imshow_hst(ax, cax, f_hst):
    from scipy.ndimage import gaussian_filter
    d_hst = gaussian_filter(f_hst[0].data.astype("d"), 1.5)
    im_hst = ax.imshow(d_hst,
                       origin="lower",
                       interpolation="nearest",
                       cmap=colormap)

    im_hst.set_clim(0.0022, 0.0087)

    if cax:
        cax.colorbar(im_hst)
        cax.axis[:].toggle(all=False)
        cax.axis["top"].toggle(ticks=True)

    return im_hst

def imshow_kpno(ax, cax, f_kpno):
    im_kpno = ax.imshow_affine(f_kpno[0].data,
                               origin="lower", cmap=colormap,
                               interpolation="nearest",
                               )
    im_kpno.set_clim(39, 90)
    if cax:
        cax.colorbar(im_kpno)
        cax.axis[:].toggle(all=False)
        cax.axis["top"].toggle(ticks=True)

    return im_kpno


def draw_figure(fig, rect, setup_axes):
    f_kpno = pyfits.open("tycho_kpno_2007_knotg.fits")
    f_hst = pyfits.open("tycho_5_drz_sci2_knotg.fits")

    gh = pywcsgrid2.GridHelper(wcs=f_hst[0].header)
    axes_kwargs = dict(grid_helper=gh)

    ax1, ax2 = setup_axes(fig, rect=rect,
                          axes_class=pywcsgrid2.Axes, axes_kwargs=axes_kwargs)

    # draw data

    im_hst = imshow_hst(ax1, ax1.cax, f_hst)

    ax1.set_xlim(118.5, 1130.5)
    ax1.set_ylim(47.5, 1422.5)


    im_kpno = imshow_kpno(ax2[f_kpno[0].header], ax2.cax, f_kpno)

    ax2.set_xlim(118.5, 1130.5)
    ax2.set_ylim(47.5, 1422.5)
    # add an inset

    
    ax3 = setup_inset_axes(ax1, f_hst, zoom=4, loc=4)

    im_hst2 = imshow_hst(ax3, None, f_hst)
    im_hst2.set_clim(0.0028, 0.0187)
    ax3.set(xlim=(592,656+10),
            ylim=(803,890))

    # adjust the location
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset
    p = mark_inset(ax1, ax3, loc1=1, loc2=3, alpha=0.5)
    p[0].set(fc="none")

    ax3.add_size_bar(1/3600./f_hst[0].header["cdelt2"],
                     r"$1^{\prime\prime}$", loc=3,
                     borderpad=0.2)



    return ax1, ax2, ax3

if 1:
    
    use_path_effect = True
    try:
        from matplotlib.patheffects import withStroke
    except ImportError:
        use_path_effect = False

    if use_path_effect:
        def add_path_effect(txt):
            txt.set_path_effects([withStroke(linewidth=3, foreground="w")])
    else:
        def add_path_effect(txt):
            pass
            
    fig = plt.figure(1, figsize=(6, 8))

    # first figure
    ax1, ax2, ax3 = draw_figure(fig, 211, setup_axes01)

    t1 = ax1.add_inner_title("(a) HST", 2, frameon=False)
    add_path_effect(t1.txt._text)

    t2 = ax2.add_inner_title("(b) KPNO", 2, frameon=False)
    add_path_effect(t2.txt._text)

    # second figure
    ax1, ax2, ax3 = draw_figure(fig, 212, setup_axes02)
    ax2.get_axes_locator().loc = 1
    ax2.axis[:].toggle(all=False)
    
    t1 = ax1.add_inner_title("HST", 2, frameon=False)
    add_path_effect(t1.txt._text)

    t2 = ax2.add_inner_title("KPNO", 9, frameon=False,
                             borderpad=0.,
                             )
    add_path_effect(t2.txt._text)

    plt.show()


