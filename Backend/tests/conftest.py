import pytest
from app.schemas import RoomDetection, RoomDirection, Direction, Compass, ComplianceRule


@pytest.fixture
def sample_room_detections():
    """Sample room detections for testing"""
    return [
        RoomDetection(label="bedroom", confidence=0.9, bbox=[100, 200, 150, 250]),
        RoomDetection(label="kitchen", confidence=0.85, bbox=[200, 100, 250, 150]),
        RoomDetection(label="toilet", confidence=0.8, bbox=[300, 200, 350, 250])
    ]


@pytest.fixture
def sample_room_directions():
    """Sample room directions for testing"""
    return [
        RoomDirection(room="bedroom", direction=Direction.SW),
        RoomDirection(room="kitchen", direction=Direction.SE),
        RoomDirection(room="toilet", direction=Direction.NW)
    ]


@pytest.fixture
def sample_compass():
    """Sample compass orientation"""
    return Compass(rotation_angle=45.0)


@pytest.fixture
def mock_rules():
    """Mock compliance rules for testing"""
    return [
        ComplianceRule(
            room="bedroom",
            preferred_directions=[Direction.N, Direction.E],
            weight=1.0,
            penalty=0.0
        ),
        ComplianceRule(
            room="kitchen",
            preferred_directions=[Direction.SE, Direction.S],
            weight=1.0,
            penalty=0.0
        ),
        ComplianceRule(
            room="toilet",
            preferred_directions=[Direction.NW, Direction.W],
            weight=1.0,
            penalty=0.0
        )
    ]


@pytest.fixture
def mock_kitchen_rule():
    """Mock rule for kitchen placement testing"""
    return {
        "rule_id": "kitchen_placement",
        "rule_name": "Kitchen Placement",
        "applicable_room_types": ["kitchen"],
        "preferred_directions": ["SE", "E"],
        "weight": 2.0,
        "penalty_factor": 1.5,
        "partial_allowed": False,
        "explanation_template": "Kitchen should be in {preferred} for optimal energy. Detected in {detected}. Compliance: {compliance_level}."
    }


@pytest.fixture
def mock_bedroom_rule():
    """Mock rule for bedroom placement testing"""
    return {
        "rule_id": "bedroom_placement",
        "rule_name": "Bedroom Placement",
        "applicable_room_types": ["bedroom"],
        "preferred_directions": ["SW", "W"],
        "weight": 1.5,
        "penalty_factor": 1.2,
        "partial_allowed": True,
        "explanation_template": "Bedrooms should be in {preferred} for restful sleep. {correct_count}/{total_count} bedrooms compliant. Compliance: {compliance_level}."
    }
# Reviewed
