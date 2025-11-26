"""
Constraint Checking for Interior Optimization
"""

from .geometry import create_furniture_polygon, check_intersection, check_containment, calculate_overlap_area

class ConstraintChecker:
    def __init__(self, room_poly, doors, windows):
        self.room_poly = room_poly
        self.doors = doors
        self.windows = windows
        
        # Create polygons for doors (clearance zones)
        self.door_polys = []
        for door in doors:
            # Create a semi-circle or rectangle clearance zone for the door
            # For simplicity, we use a rectangle extending into the room
            # This requires knowing wall orientation, which we can infer or pass
            pass # TODO: Implement door clearance generation

    def create_furniture_polygon_wrapper(self, item, x, y, rot):
        """Wrapper to create polygon from item dict"""
        return create_furniture_polygon(x, y, item["width"], item["depth"], rot)

    def check_boundary(self, furniture_poly):
        """Check if furniture is fully inside the room"""
        return check_containment(self.room_poly, furniture_poly)

    def check_overlap(self, furniture_poly, other_polys):
        """Check if furniture overlaps with any other furniture"""
        for other in other_polys:
            if check_intersection(furniture_poly, other):
                # Allow slight touching? No, strict no-overlap for now
                if calculate_overlap_area(furniture_poly, other) > 0.01: # Tolerance
                    return True
        return False

    def check_door_blocking(self, furniture_poly):
        """Check if furniture blocks a door"""
        # For now, check distance to door positions
        # TODO: Implement robust door blocking check
        return False

    def check_window_blocking(self, furniture_poly, furniture_height):
        """Check if tall furniture blocks a window"""
        # If furniture is low (e.g. bed, table), it might be okay
        # If tall (wardrobe), it shouldn't be in front of window
        pass

    def check_hard_constraints(self, furniture_poly, other_polys):
        """
        Check all hard constraints (must be satisfied).
        Returns True if valid, False otherwise.
        """
        if not self.check_boundary(furniture_poly):
            return False
        if self.check_overlap(furniture_poly, other_polys):
            return False
        return True

    def get_nearest_wall_distance(self, furniture_poly):
        """Get distance to nearest wall"""
        from .geometry import distance_to_wall
        # Use centroid for distance
        return distance_to_wall(furniture_poly.centroid, self.room_poly)
