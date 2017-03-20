

from matplotlib import pyplot as plt

from config import DxfConfig

def plotCircle(circle, ax, _color):

    x, y, z = circle.center
    r = circle.radius

    c = plt.Circle((x, y), r, color=_color, fill=False)
    ax.add_artist(c)


def plotPolyline(polyline, ax, _color):

    # See http://www.afralisp.net/archive/lisp/Bulges1.htm for how to decode bulges

    points = polyline.points
    if polyline.is_closed:
        points.append(polyline.points[0])

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    ax.plot(xs, ys, color=_color, linewidth=1, solid_capstyle='round')
    ax.set_aspect('equal')


def plotEntity(entity, ax, color):

    if entity.dxftype == DxfConfig.POLYLINE or entity.dxftype == DxfConfig.LWPOLYLINE:
        plotPolyline(entity, ax, color)
    elif entity.dxftype == DxfConfig.CIRCLE:
        plotCircle(entity, ax, color)


def plotLayer(entities, layerName, ax, color='b', xlim=(-6000, 6000), ylim=(-18000, 18000)):

    for entity in entities:
        plotEntity(entity, ax, color)

    ax.set_title(layerName)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

def plotAllLayers(layers, layersToPlot=[DxfConfig.SU8_1, DxfConfig.SU8_2,
                                        DxfConfig.SU8_3, DxfConfig.METAL,
                                        DxfConfig.VPORT],
                  xlim=(-6000, 6000), ylim=(-18000, 18000)):

    fig, axes = plt.subplots(1, 5, subplot_kw=dict(aspect='equal'),
                                figsize=(16, 6), dpi=90)

    fig.tight_layout()
    plt.subplots_adjust(top=0.9)

    for i, layer in enumerate(layersToPlot):
        plotLayer(layers[layer], layer, axes[i], xlim=xlim, ylim=ylim)

    plt.show()

def plotPolylines(polylines):

    fig, axes = plt.subplots()

    for polyline in polylines:
        plotEntity(polyline, axes, 'r')

    plt.show()
