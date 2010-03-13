import matplotlib.pyplot as plt
import pyfits

from mpl_toolkits.axisartist.grid_finder import FixedLocator
from mpl_toolkits.axisartist.floating_axes import floatingaxes_class_factory

from mpl_toolkits.axisartist.angle_helper import LocatorDMS, LocatorHMS, \
     FormatterHMS, FormatterDMS

from pywcsgrid2.axes_wcs import GridHelperWcsFloating, AxesWcs

import matplotlib.axes as maxes

use_path_effects = True
try:
    import matplotlib.patheffects
except ImportError:
    use_path_effects = False



def allsky_header():
    # header retrieved from "lambda_mollweide_halpha_fwhm06_0512.fits"
    header = """XTENSION= 'IMAGE   '           / IMAGE extension
BITPIX  =                  -32 / Number of bits per data pixel
NAXIS   =                    2 / Number of data axes
NAXIS1  =                 4096 /
NAXIS2  =                 2048 /
PCOUNT  =                    0 / No Group Parameters
GCOUNT  =                    1 / One Data Group
EXTNAME = 'TEMPERATURE'
CTYPE1  = 'GLON-MOL'           / Coordinate Type
CTYPE2  = 'GLAT-MOL'           / Coordinate Type
EQUINOX =              2000.00 / Equinox of Ref. Coord.
CDELT1  =     -0.0791293637247 / Degrees / Pixel
CDELT2  =      0.0791293637247 / Degrees / Pixel
CROTA2  =              0.00000 / Rotation Angle (Degrees)
CRPIX1  =              2048.50 / Reference Pixel in X
CRPIX2  =              1024.50 / Reference Pixel in Y
CRVAL1  =        0.00000000000 / Galactic longitude of reference pixel
CRVAL2  =        0.00000000000 / Galactic latitude of reference pixel
LONPOLE =        0.00000000000 / Native longitude of Galactic pole
LATPOLE =        0.00000000000 / Galactic latitude of native pole
PV2_1   =        0.00000000000 /Projection parameter 1
HISTORY PUTAST: Jun 17 14:36:35 2009 World Coordinate System parameters written
"""
    cards = pyfits.CardList()
    for l in header.split("\n"):
        card = pyfits.Card()
        card.fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h



if 1:
    import os.path

    fits_name = "lambda_mollweide_halpha_fwhm06_0512.fits"
    if os.path.exists(fits_name):
        f = pyfits.open(fits_name)
        data = f[1].data
        header = f[1].header
    else:
        data = None
        header = allsky_header()


    fig = plt.figure(1, figsize=(8, 5))
    fig.clf()

    FloatingAxes = floatingaxes_class_factory(AxesWcs)
    FloatingSubplot = maxes.subplot_class_factory(FloatingAxes)


    grid_locator1 = FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    grid_locator2 = FixedLocator([-90, -60, -30, 0, 30, 60, 90])
    tick_formatter1=FormatterHMS()
    tick_formatter2=FormatterDMS()

    grid_helper = GridHelperWcsFloating(wcs=header,
                                        extremes=(-180, 180, -90, 90),
                                        grid_locator1=grid_locator1,
                                        grid_locator2=grid_locator2,
                                        tick_formatter1=tick_formatter1,
                                        tick_formatter2=tick_formatter2,
                                        )

    ax = FloatingSubplot(fig, 111, grid_helper=grid_helper)
    ax.set_autoscale_on(False)
    fig.add_subplot(ax)

    if data is not None:
        im = ax.imshow(data, origin="lower", cmap=plt.cm.gray_r)
        im.set_clip_path(ax.patch)
        im.set_clim(0, 30)

    #for an in ["bottom", "top"]:
    ax.axis["bottom", "top"].set_visible(False)

    ax.axis["right"].set_axis_direction("left")

    axis = ax.axis["left"]
    axis.set_axis_direction("right")
    axis.major_ticklabels._text_follow_ref_angle=False
    axis.major_ticklabels.set(rotation=0,
                              va="center", ha="center",
                              pad=0)
    axis.label._text_follow_ref_angle=False
    axis.label.set(rotation=0, va="center", ha="right")


    ax.axis["b=0"] = grid_helper.new_floating_axis(nth_coord=1, value=0,
                                                   axes=ax,
                                                   axis_direction='bottom')

    axis = ax.axis["b=0"]
    axis.get_helper().set_extremes(-180, 180)

    if use_path_effects:
        ef = matplotlib.patheffects.withStroke(foreground="w", linewidth=3)
        axis.major_ticklabels.set_path_effects([ef])
        axis.label.set_path_effects([ef])

    ax.grid()
    plt.show()

