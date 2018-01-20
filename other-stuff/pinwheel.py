import numpy as np
import math
import matplotlib.pyplot as plt
import shapely.geometry
import shapely.affinity
import shapely.ops
import copy

import geopandas as gpd

class PW_triangle():
    small_angle = np.arctan(0.5)
    big_angle = np.pi / 2 - small_angle
    def __init__(self, pw=None, handedness=1, origin=(0., 0., 0.), angle=0., scale=1.):
        self.handedness = handedness
        if self.handedness == 1:
            self.poly = shapely.geometry.polygon.Polygon([(0., 0.), (2., 0.), (2., 1.)])
        else:
            self.poly = shapely.geometry.polygon.Polygon([(0., 1.), (2., 1.), (2., 0.)])
        self.poly = shapely.affinity.translate(self.poly, xoff=origin[0], yoff=origin[1])
        self.rotate(angle)
        self.scale(scale)
        
        return
    
    def rotate(self, angle, use_radians=False):
        self.poly = shapely.affinity.rotate(self.poly, angle, 
                                            origin=self.poly.exterior.coords[0], 
                                            use_radians=use_radians)
    
    def scale(self, scale):
        xo, yo = self.poly.exterior.coords[0]
        self.poly = shapely.affinity.scale(self.poly, xfact=scale, yfact=scale, origin=(xo, yo, 0.))
        
    def edge_vector(self, i=0):
        p0 = self.poly.exterior.coords[i]
        p1 = self.poly.exterior.coords[(i+1) % 3]
        return (p1[0] - p0[0], p1[1] - p0[1])
    
    def mirror_in_edge(self, i=0):
        xo, yo = self.poly.exterior.coords[i]
        self.poly = shapely.affinity.translate(self.poly, xoff=-xo, yoff=-yo)
        ev = self.edge_vector(i=i)
        angle = np.arctan2(ev[1], ev[0])
        self.rotate(-angle, use_radians=True)
        self.poly = shapely.affinity.scale(self.poly, xfact=1., yfact=-1., origin=(0., 0., 0.))
        self.rotate(angle, use_radians=True)
        self.poly = shapely.affinity.translate(self.poly, xoff=xo, yoff=yo)
        self.handedness = -self.handedness
    
    def slide_along_edge(self, i=0, forward=True):
        translation = self.edge_vector(i=i)
        if forward:
            self.poly = shapely.affinity.translate(self.poly, xoff=translation[0], yoff=translation[1])
        else:
            self.poly = shapely.affinity.translate(self.poly, xoff=-translation[0], yoff=-translation[1])
        
    def deflate(self):
        t1 = copy.deepcopy(self)
        t1.mirror_in_edge()
        t1.slide_along_edge()
        t1.rotate(t1.handedness * (np.pi + self.big_angle), use_radians=True)
        t1.scale(1. / np.sqrt(5.))
        
        t2 = copy.deepcopy(self)
        t2.mirror_in_edge()
        t2.rotate(-t2.handedness * self.small_angle, use_radians=True)
        t2.scale(1. / np.sqrt(5.))
        
        t3 = copy.deepcopy(t2)
        t3.slide_along_edge(2, forward=False)

        t4 = copy.deepcopy(t3)
        t4.mirror_in_edge()
        
        t5 = copy.deepcopy(t4)
        t5.rotate(180)
        t5.slide_along_edge(2)
        
        return [t1, t2, t3, t4, t5]
    
    def inflate(self):
        t1 = copy.deepcopy(self)
        
        t2 = copy.deepcopy(t1)
        t2.rotate(180)
        t2.slide_along_edge(2)
        
        t3 = copy.deepcopy(t1)
        t3.mirror_in_edge()
        
        t4 = copy.deepcopy(t3)
        t4.slide_along_edge(2)
        
        t5 = copy.deepcopy(t3)
        t5.slide_along_edge(2, forward=False)
        t5.rotate(90)
        
        result = [t1, t2, t3, t4, t5]
        
        return result, t1.dissolve(result[1:])
    
    def dissolve(self, others):
        new = copy.deepcopy(self)
        merged = shapely.ops.unary_union([self.poly] + [__.poly for __ in others])
        if type(merged) != shapely.geometry.polygon.Polygon:
            merged = merged.geoms[0]
        new.poly = merged
        return new

pwt = PW_triangle(handedness=1, scale=100)

triangles, next_pwt = pwt.inflate()
triangles, next_pwt = next_pwt.inflate()
#triangles, next_triangle = next_triangle.inflate()
tiling = gpd.GeoDataFrame(geometry=gpd.GeoSeries([next_pwt.poly] + [__.poly for __ in triangles]))
tiling.plot()
print(next_pwt.poly)