"""
Geometry Utilities for Interior Optimization
Uses Shapely for robust geometric operations.
"""

from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import rotate, translate
import math

def create_furniture_polygon(x, y, width, depth, angle):
    """
    Create a shapely Polygon for a furniture item.
    x, y: Center position
    width, depth: Dimensions
    angle: Rotation in degrees
    """
    # Create rectangle centered at (0,0)
    half_w = width / 2
    half_d = depth / 2
    coords = [
        (-half_w, -half_d),
        (half_w, -half_d),
        (half_w, half_d),
        (-half_w, half_d)
    ]
    poly = Polygon(coords)
    
    # Rotate
    if angle != 0:
        poly = rotate(poly, angle, origin=(0, 0))
    
    # Translate to position
    poly = translate(poly, x, y)
    return poly

def create_room_polygon(coords):
    """Create a shapely Polygon for the room from a list of [x, y] points"""
    return Polygon(coords)

def check_intersection(poly1, poly2):
    """Check if two polygons intersect (overlap)"""
    return poly1.intersects(poly2)

def check_containment(container, item):
    """Check if item is fully inside container"""
    return container.contains(item)

def calculate_overlap_area(poly1, poly2):
    """Calculate area of intersection between two polygons"""
    if not poly1.intersects(poly2):
        return 0.0
    return poly1.intersection(poly2).area

def distance_to_wall(point, room_poly):
    """Calculate minimum distance from a point to the room boundary"""
    p = Point(point)
    return room_poly.boundary.distance(p)

def get_nearest_wall_edge(poly, room_poly):
    """Find which wall of the room is closest to the furniture"""
    # This is a simplified version; for complex rooms, we check distance to each segment
    return room_poly.boundary.distance(poly)
