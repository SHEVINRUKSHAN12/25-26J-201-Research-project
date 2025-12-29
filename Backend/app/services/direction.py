import math
from typing import List
from app.schemas import RoomDetection, Direction, RoomDirection, Compass
from app.services.orientation import compute_floor_center, rotate_vector


def calculate_room_directions(detections: List[RoomDetection], compass: Compass) -> List[RoomDirection]:
    """
    Calculate the cardinal direction for each detected room relative to the floor center and compass orientation.
    """
    if not detections:
        return []
    
    center_x, center_y = compute_floor_center(detections)
    room_directions = []
    
    for detection in detections:
        bbox = detection.bbox
        room_center_x = (bbox[0] + bbox[2]) / 2
        room_center_y = (bbox[1] + bbox[3]) / 2
        
        # Vector from floor center to room center
        dx = room_center_x - center_x
        dy = room_center_y - center_y
        
        # Rotate to align with true North
        rotated_dx, rotated_dy = rotate_vector(dx, dy, compass.rotation_angle)
        
        # Calculate angle (0 = North, 90 = East, etc.)
        # Use atan2 with -rotated_dy to account for image coordinates (y down)
        angle_rad = math.atan2(-rotated_dy, rotated_dx)
        angle_deg = math.degrees(angle_rad) % 360
        
        direction = get_direction_from_angle(angle_deg)
        room_directions.append(RoomDirection(room=detection.label, direction=direction))
    
    return room_directions


def get_direction_from_angle(angle_deg: float) -> Direction:
    """
    Map an angle in degrees to a cardinal direction.
    0-22.5: N, 22.5-67.5: NE, etc.
    """
    # Normalize angle to 0-360 range
    normalized_angle = angle_deg % 360
    if normalized_angle < 0:
        normalized_angle += 360
    
    if 337.5 <= normalized_angle or normalized_angle < 22.5:
        return Direction.N
    elif 22.5 <= normalized_angle < 67.5:
        return Direction.NE
    elif 67.5 <= normalized_angle < 112.5:
        return Direction.E
    elif 112.5 <= normalized_angle < 157.5:
        return Direction.SE
    elif 157.5 <= normalized_angle < 202.5:
        return Direction.S
    elif 202.5 <= normalized_angle < 247.5:
        return Direction.SW
    elif 247.5 <= normalized_angle < 292.5:
        return Direction.W
    elif 292.5 <= normalized_angle < 337.5:
        return Direction.NW
    else:
        return Direction.N  # Fallback
# Reviewed
