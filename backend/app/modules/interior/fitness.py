"""
Fitness Function for Interior Optimization
Calculates the score of a given furniture layout.
"""

from .geometry import calculate_overlap_area, check_containment
from .constraints import ConstraintChecker

class FitnessEvaluator:
    def __init__(self, room_poly, furniture_items, constraints: ConstraintChecker):
        self.room_poly = room_poly
        self.furniture_items = furniture_items
        self.constraints = constraints
        self.room_area = room_poly.area

    def calculate_fitness(self, layout):
        """
        Calculate fitness score for a layout.
        layout: List of (x, y, rotation) for each furniture item
        Returns: float score (higher is better)
        """
        score = 0.0
        
        # 1. Hard Constraints (Penalties)
        penalty = 0.0
        furniture_polys = []
        
        # Create polygons for current layout
        for i, item in enumerate(self.furniture_items):
            x, y, rot = layout[i]
            poly = self.constraints.create_furniture_polygon_wrapper(item, x, y, rot) # Helper needed
            furniture_polys.append(poly)
            
            # Boundary check
            if not self.constraints.check_boundary(poly):
                penalty += 1000 # Heavy penalty for being outside
            
        # Overlap check
        for i in range(len(furniture_polys)):
            for j in range(i + 1, len(furniture_polys)):
                overlap = calculate_overlap_area(furniture_polys[i], furniture_polys[j])
                if overlap > 0:
                    penalty += overlap * 500 # Penalty proportional to overlap area
                    
        # If hard constraints violated, return low score
        if penalty > 0:
            return -penalty
            
        # 2. Space Utilization
        # We want to maximize usable space, but also efficient placement
        # For now, let's reward keeping center open (distance from center?)
        # Or alignment with walls
        
        alignment_score = 0
        for poly in furniture_polys:
            # Check distance to nearest wall
            dist = self.constraints.get_nearest_wall_distance(poly)
            if dist < 0.1: # Close to wall
                alignment_score += 10
                
        score += alignment_score
        
        # 3. Functional Grouping (e.g. Bed near side table)
        # TODO: Implement adjacency bonuses
        
        return score

    def calculate_normalized_score(self, raw_fitness):
        """
        Convert raw fitness to a 0-100% score for user display.
        """
        if raw_fitness < 0:
            # Penalty case: Map negative values to 0-50%
            # A small penalty should drop it to 40%, large to 0%
            return max(0.0, 50.0 + (raw_fitness * 0.1))
        else:
            # Positive case: Map 0-Max to 50-100%
            # Max possible alignment score is roughly num_items * 10
            max_score = len(self.furniture_items) * 10
            if max_score == 0: return 50.0
            
            percentage = 50.0 + (raw_fitness / max_score) * 50.0
            return min(100.0, percentage)
