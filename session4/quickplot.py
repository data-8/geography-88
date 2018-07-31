import matplotlib
import matplotlib.pyplot as plt
import shapely.geometry
import matplotlib.collections as mpc
from matplotlib.patches import Polygon
from matplotlib.path import Path
from matplotlib.lines import Line2D
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
    lines = []
    newvals = []
    geoms = gdf.geometry
    if column is not None:
        values = gdf[column]
    else:
        values = None

    for linenum in range(len(geoms)):
        line = geoms.iloc[linenum]
        if type(line) == shapely.geometry.multilinestring.MultiLineString:
            for currline in line.geoms:
                #x = [__[0] for __ in currline.coords]
                #y = [__[1] for __ in currline.coords]
                #lines.append(Line2D(x, y))
                lines.append(np.asarray(currline.coords))
                if values is not None:
                    newvals.append(values.iloc[linenum])
        elif type(line) == shapely.geometry.linestring.LineString:
            #x = [__[0] for __ in line.coords]
            #y = [__[1] for __ in line.coords]
            #lines.append(Line2D(x, y))
            lines.append(np.asarray(line.coords))
            if values is not None:
                newvals.append(values.iloc[linenum])
        else: pass

    lines = mpc.LineCollection(lines, facecolors='none', linewidth=linewidth,
                                  edgecolor=edgecolor, alpha=alpha, **kwargs)
    if values is not None:
        lines.set_array(np.asarray(values))
        lines.set_cmap(cmap)
        norm = matplotlib.colors.Normalize()
        norm.autoscale(values)
        lines.set_norm(norm)
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

    elif layer_type == shapely.geometry.linestring.LineString or layer_type == shapely.geometry.multilinestring.MultiLineString:
        plot_lines(gdf, column, cmap, facecolor, edgecolor, alpha, linewidth, **kwargs)

    else:
        plot_polygons(gdf, column, cmap, facecolor, edgecolor, alpha, linewidth, **kwargs)