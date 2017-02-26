import shapely
import math
import geopandas as gpd

# makes hex centers for the specified bounding box and number of rows
def make_centers(xmin=-180, xmax=180, ymin=-85, ymax=85, nrows=10):
    row_spacing = (ymax - ymin) / nrows
    col_spacing = 2 / math.sqrt(3) * row_spacing
    ncols = (xmax - xmin) / col_spacing
    x = []
    y = []
    for r in range(int(nrows + 0.5)):
        offset = 0.5 * (r % 2)
        x += [(c + 0.25 + offset) * col_spacing + xmin for c in range(int(ncols + 0.5))] 
        y += [(r + 0.5) * row_spacing + ymin] * int(ncols + 0.5)
    return (x, y)

# makes hexagons returning a list of shapely.geometry.polygon.Polygons
# first calls make_centers to determine hexagon centers 
def make_hexes(xmin=-175, xmax=175, ymin=-85, ymax=85, nrows=10):
    centers = make_centers(xmin, xmax, ymin, ymax, nrows)
    radius = (centers[0][1] - centers[0][0]) / math.sqrt(3)
    hexes = []
    for (x, y) in zip(centers[0], centers[1]):
        this_hex = []
        for theta in [(1/6 + i/3) * math.pi for i in range(6)]:
            this_hex.append((x + radius * math.cos(theta), y + radius * math.sin(theta)))
        hexes.append(shapely.geometry.polygon.Polygon(this_hex))
    return hexes

def get_hexbins(pts, nrows=10):
    import geopandas as gpd
    
    b = pts.bounds
    hexes = gpd.GeoSeries(make_hexes(nrows=nrows, 
                                     xmin=min(b.minx), 
                                     xmax=max(b.maxx), 
                                     ymin=min(b.miny), 
                                     ymax=max(b.maxy)))
    hexes.crs = pts.crs
    return gpd.GeoDataFrame(geometry=hexes)

def hexbin_density(pts, nrows=10):
    pts['count'] = 1
    hb = get_hexbins(pts, nrows=nrows)
    p_counts = gpd.sjoin(pts, hb, how='inner', op='within')[['index_right', 'count']].groupby(['index_right'], as_index=False).sum()
    p_density = hb.merge(p_counts, how='inner', left_index=True, right_on='index_right')[['geometry', 'count']]
    return p_density, hb


