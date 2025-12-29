import math
from typing import List, Tuple
from app.schemas import RoomDetection, Direction


def compute_floor_center(detections: List[RoomDetection]) -> Tuple[float, float]:
    """
    Compute the geometric center of the floor plan based on room bounding boxes.
    This serves as the reference point for direction calculations.
    """
    if not detections:
        return 0.0, 0.0
    
    centers = []
    for detection in detections:
        bbox = detection.bbox
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        centers.append((center_x, center_y))
    
    avg_x = sum(x for x, y in centers) / len(centers)
    avg_y = sum(y for x, y in centers) / len(centers)
    return avg_x, avg_y


def rotate_vector(dx: float, dy: float, angle_deg: float) -> Tuple[float, float]:
    """
    Rotate a vector by the given angle (degrees) to align with true North.
    Negative angle for clockwise rotation (compass convention).
    """
    angle_rad = math.radians(-angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rotated_dx = dx * cos_a - dy * sin_a
    rotated_dy = dx * sin_a + dy * cos_a
    return rotated_dx, rotated_dy


class OrientationService:
    """Service for managing compass orientation and manual overrides"""

    def __init__(self):
        self.manual_angle: float = 0.0
        self.override_automatic: bool = False

    def set_manual_angle(self, angle: float) -> bool:
        """Set manual compass angle in degrees"""
        if 0.0 <= angle <= 360.0:
            self.manual_angle = angle
            self.override_automatic = True
            return True
        return False

    def direction_to_angle(self, direction: Direction) -> float:
        """Convert cardinal direction to angle in degrees"""
        direction_angles = {
            Direction.N: 0.0,
            Direction.NE: 45.0,
            Direction.E: 90.0,
            Direction.SE: 135.0,
            Direction.S: 180.0,
            Direction.SW: 225.0,
            Direction.W: 270.0,
            Direction.NW: 315.0
        }
        return direction_angles.get(direction, 0.0)

    def get_current_angle(self) -> float:
        """Get current compass angle"""
        return self.manual_angle if self.override_automatic else 0.0
# Reviewed
