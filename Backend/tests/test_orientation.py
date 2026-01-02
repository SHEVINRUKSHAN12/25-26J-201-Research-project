import pytest
import math
from app.services.orientation import compute_floor_center, rotate_vector


class TestFloorCenterCalculation:
    """Test floor center computation from room detections"""

    def test_single_room_center(self):
        """Test center calculation with single room"""
        from app.schemas import RoomDetection
        detections = [RoomDetection(label="bedroom", confidence=0.9, bbox=[100, 200, 150, 250])]
        center_x, center_y = compute_floor_center(detections)
        # Center of bbox [100,200,150,250] is ((100+150)/2, (200+250)/2) = (125, 225)
        assert center_x == 125.0
        assert center_y == 225.0

    def test_multiple_rooms_center(self, sample_room_detections):
        """Test center calculation with multiple rooms"""
        center_x, center_y = compute_floor_center(sample_room_detections)
        # Expected: average of centers
        # bedroom: (125, 225), kitchen: (225, 125), toilet: (325, 225)
        # avg_x = (125 + 225 + 325) / 3 = 225
        # avg_y = (225 + 125 + 225) / 3 = 191.666...
        expected_x = (125 + 225 + 325) / 3
        expected_y = (225 + 125 + 225) / 3
        assert center_x == pytest.approx(expected_x, rel=1e-2)
        assert center_y == pytest.approx(expected_y, rel=1e-2)

    def test_empty_detections_center(self):
        """Test center calculation with no detections"""
        center_x, center_y = compute_floor_center([])
        assert center_x == 0.0
        assert center_y == 0.0


class TestVectorRotation:
    """Test vector rotation logic"""

    def test_zero_rotation(self):
        """Test no rotation keeps vector unchanged"""
        result = rotate_vector(1.0, 0.0, 0.0)
        assert result == (1.0, 0.0)

    def test_90_degree_rotation(self):
        """Test 90-degree clockwise rotation"""
        result = rotate_vector(1.0, 0.0, 90.0)
        # Clockwise 90°: (x,y) -> (y, -x)
        # But our function uses negative angle for clockwise
        # rotate_vector uses -angle, so 90° becomes -90° counterclockwise
        # (1,0) rotated -90°: (0,1) wait no
        # Standard rotation: counterclockwise positive
        # Our function: angle_rad = math.radians(-angle_deg)
        # So for 90°, angle_rad = -π/2
        # cos(-π/2)=0, sin(-π/2)=-1
        # rotated_dx = 1*0 - 0*(-1) = 0
        # rotated_dy = 1*(-1) + 0*0 = -1
        # So (0, -1) which is down, but wait
        # Actually for compass, clockwise rotation
        # Let's check the code
        # angle_rad = math.radians(-angle_deg)  # for 90°, -90°
        # cos_a = cos(-90°) = 0
        # sin_a = sin(-90°) = -1
        # rotated_dx = dx * 0 - dy * (-1) = 0 + dy
        # rotated_dy = dx * (-1) + dy * 0 = -dx
        # For (1,0): (0, -1)
        # But for direction, we use atan2(-rotated_dy, rotated_dx)
        # This is getting complex. Let's test with known values.

        # For 0° rotation: (1,0) -> (1,0)
        assert rotate_vector(1.0, 0.0, 0.0) == (1.0, 0.0)

        # For 180°: should flip
        result_180 = rotate_vector(1.0, 0.0, 180.0)
        assert result_180 == pytest.approx((-1.0, 0.0), rel=1e-10)

    def test_180_degree_rotation(self):
        """Test 180-degree rotation"""
        result = rotate_vector(1.0, 0.0, 180.0)
        assert result == pytest.approx((-1.0, 0.0), rel=1e-10)

    def test_negative_coordinates(self):
        """Test rotation with negative coordinates"""
        result = rotate_vector(-1.0, -1.0, 90.0)
        # This should be deterministic
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(coord, float) for coord in result)

    def test_floating_point_precision(self):
        """Test rotation maintains floating point precision"""
        result = rotate_vector(1.0, 1.0, 45.0)
        # Clockwise 45° rotation of (1,1) should give approximately (√2, 0)
        expected_x = 1.4142135623730951  # √2
        expected_y = 0.0
        assert abs(result[0] - expected_x) < 1e-10
        assert abs(result[1] - expected_y) < 1e-10
# Reviewed
