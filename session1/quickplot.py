import matplotlib
import matplotlib.pyplot as plt
import shapely.geometry
import matplotlib.collections as mpc
from matplotlib.patches import Polygon
from matplotlib.path import Path
import numpy as np


def plot_polygons(gdf, column=None, cmap='Set1', facecolor=None, edgecolor=None,
                            alpha=1.0, linewidth=0.5, **kwargs):
    # Makes a MatPlotLib PatchCollection out of Polygon and/or MultiPolygon geometries 
    # Thanks to http://stackoverflow.com/a/33753927

    patches = []
    newvals = []
    geoms = gdf.geometry
    if column is not None:
        values = gdf[column]
    else:
        values = None

    for polynum in range(len(geoms)):
        poly = geoms.iloc[polynum]
        if type(poly) != shapely.geometry.polygon.Polygon:
            for currpoly in poly.geoms:
                a = np.asarray(currpoly.exterior)
                patches.append(Polygon(a))
                if values is not None:
                    newvals.append(values.iloc[polynum])
        else:
            a = np.asarray(poly.exterior)
            patches.append(Polygon(a))
            if values is not None:
                newvals.append(values.iloc[polynum])

    patches = mpc.PatchCollection(patches, facecolor=facecolor, linewidth=linewidth,
                                  edgecolor=edgecolor, alpha=alpha, **kwargs)
    if values is not None:
        patches.set_array(np.asarray(newvals))
        patches.set_cmap(cmap)
        norm = matplotlib.colors.Normalize()
        norm.autoscale(newvals)
        patches.set_norm(norm)
    plt.gca().add_collection(patches, autolim=True)
    plt.gca().set_aspect('equal')
    plt.gca().autoscale_view()
    return patches


def plot_lines(gdf, column=None, cmap='Set1', facecolor=None, edgecolor=None,
                            alpha=1.0, linewidth=0.5, **kwargs):

    geoms = gdf.geometry
    lines = [Path(np.asarray(line)) for line in geoms]

    if column is not None:
        values = gdf[column]
    else:
        values = None

    lines = mpc.PathCollection(lines, facecolor=facecolor, linewidth=linewidth,
                                  edgecolor=edgecolor, alpha=alpha, **kwargs)
    if values is not None:
        patches.set_array(np.asarray(values))
        patches.set_cmap(cmap)
        norm = matplotlib.colors.Normalize()
        norm.autoscale(values)
        patches.set_norm(norm)
    plt.gca().add_collection(lines, autolim=True)
    plt.gca().set_aspect('equal')
    plt.gca().autoscale_view()
    return lines


def plot_points(gdf, **kwargs):
    # Makes a MatPlotLib PatchCollection out of Polygon and/or MultiPolygon geometries
    # Thanks to http://stackoverflow.com/a/33753927

    x = [p.x for p in gdf.geometry]
    y = [p.y for p in gdf.geometry]

    plt.gca().set_aspect('equal')
    plt.gca().autoscale_view()
    plt.plot(x, y, 'k.', **kwargs)
    return zip(x, y)


def quickplot(gdf, column=None, cmap='Set1',
              facecolor=None, edgecolor=None, alpha=1.0, linewidth=0.5, **kwargs):

    layer_type = type(gdf.geometry.iloc[0])

    if layer_type == shapely.geometry.point.Point:
        plot_points(gdf, **kwargs)

    elif layer_type == shapely.geometry.linestring.LineString:
        plot_lines(gdf, column, cmap, facecolor, edgecolor, alpha, linewidth, **kwargs)

    else:
        plot_polygons(gdf, column, cmap, facecolor, edgecolor, alpha, linewidth, **kwargs)