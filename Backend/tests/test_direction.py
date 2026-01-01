import pytest
import math
from app.services.direction import get_direction_from_angle, calculate_room_directions
from app.schemas import Direction


class TestDirectionMapping:
    """Test mapping angles to cardinal directions"""

    def test_north_directions(self):
        """Test angles mapping to North"""
        assert get_direction_from_angle(0.0) == Direction.N
        assert get_direction_from_angle(15.0) == Direction.N
        assert get_direction_from_angle(22.4) == Direction.N
        assert get_direction_from_angle(337.5) == Direction.N
        assert get_direction_from_angle(359.9) == Direction.N

    def test_northeast_directions(self):
        """Test angles mapping to North-East"""
        assert get_direction_from_angle(22.5) == Direction.NE
        assert get_direction_from_angle(45.0) == Direction.NE
        assert get_direction_from_angle(67.4) == Direction.NE

    def test_east_directions(self):
        """Test angles mapping to East"""
        assert get_direction_from_angle(67.5) == Direction.E
        assert get_direction_from_angle(90.0) == Direction.E
        assert get_direction_from_angle(112.4) == Direction.E

    def test_southeast_directions(self):
        """Test angles mapping to South-East"""
        assert get_direction_from_angle(112.5) == Direction.SE
        assert get_direction_from_angle(135.0) == Direction.SE
        assert get_direction_from_angle(157.4) == Direction.SE

    def test_south_directions(self):
        """Test angles mapping to South"""
        assert get_direction_from_angle(157.5) == Direction.S
        assert get_direction_from_angle(180.0) == Direction.S
        assert get_direction_from_angle(202.4) == Direction.S

    def test_southwest_directions(self):
        """Test angles mapping to South-West"""
        assert get_direction_from_angle(202.5) == Direction.SW
        assert get_direction_from_angle(225.0) == Direction.SW
        assert get_direction_from_angle(247.4) == Direction.SW

    def test_west_directions(self):
        """Test angles mapping to West"""
        assert get_direction_from_angle(247.5) == Direction.W
        assert get_direction_from_angle(270.0) == Direction.W
        assert get_direction_from_angle(292.4) == Direction.W

    def test_northwest_directions(self):
        """Test angles mapping to North-West"""
        assert get_direction_from_angle(292.5) == Direction.NW
        assert get_direction_from_angle(315.0) == Direction.NW
        assert get_direction_from_angle(337.4) == Direction.NW

    def test_boundary_cases(self):
        """Test exact boundary angles"""
        # These should map to the next direction
        assert get_direction_from_angle(22.5) == Direction.NE  # Exactly on boundary
        assert get_direction_from_angle(67.5) == Direction.E
        assert get_direction_from_angle(112.5) == Direction.SE
        assert get_direction_from_angle(157.5) == Direction.S
        assert get_direction_from_angle(202.5) == Direction.SW
        assert get_direction_from_angle(247.5) == Direction.W
        assert get_direction_from_angle(292.5) == Direction.NW
        assert get_direction_from_angle(337.5) == Direction.N  # Wraps around

    def test_negative_angles(self):
        """Test negative angles (should be normalized)"""
        assert get_direction_from_angle(-45.0) == get_direction_from_angle(315.0)
        assert get_direction_from_angle(-90.0) == get_direction_from_angle(270.0)

    def test_large_angles(self):
        """Test angles larger than 360 degrees"""
        assert get_direction_from_angle(360.0) == Direction.N
        assert get_direction_from_angle(405.0) == get_direction_from_angle(45.0)


class TestRoomDirectionCalculation:
    """Test full room direction calculation pipeline"""

    def test_empty_detections(self, sample_compass):
        """Test with no detections"""
        result = calculate_room_directions([], sample_compass)
        assert result == []

    def test_single_room_direction(self, sample_compass):
        """Test direction calculation for single room"""
        from app.schemas import RoomDetection
        detections = [RoomDetection(label="kitchen", confidence=0.9, bbox=[0, 0, 10, 10])]
        # Room center at (5,5), floor center at (5,5), so vector (0,0)
        # After rotation by 45°, still (0,0), angle undefined, defaults to N
        result = calculate_room_directions(detections, sample_compass)
        assert len(result) == 1
        assert result[0].room == "kitchen"
        assert result[0].direction == Direction.N  # Default for zero vector

    def test_multiple_rooms_directions(self, sample_room_detections, sample_compass):
        """Test direction calculation for multiple rooms"""
        result = calculate_room_directions(sample_room_detections, sample_compass)
        assert len(result) == 3
        # All should have valid directions
        for rd in result:
            assert isinstance(rd.direction, Direction)
            assert rd.room in ["bedroom", "kitchen", "toilet"]

    def test_deterministic_output(self, sample_room_detections, sample_compass):
        """Test that same inputs produce same outputs"""
        result1 = calculate_room_directions(sample_room_detections, sample_compass)
        result2 = calculate_room_directions(sample_room_detections, sample_compass)
        assert result1 == result2

    def test_different_compass_angles(self, sample_room_detections, sample_compass):
        """Test that different compass angles produce different results"""
        compass_0 = sample_compass.__class__(rotation_angle=0.0)
        compass_90 = sample_compass.__class__(rotation_angle=90.0)
        
        result_0 = calculate_room_directions(sample_room_detections, compass_0)
        result_90 = calculate_room_directions(sample_room_detections, compass_90)
        
        # Results should be different (at least some directions)
        directions_0 = [rd.direction for rd in result_0]
        directions_90 = [rd.direction for rd in result_90]
        assert directions_0 != directions_90  # Should differ due to rotation