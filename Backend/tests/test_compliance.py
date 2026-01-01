import pytest
from app.services.compliance import ComplianceEngine
from app.schemas import Direction, RoomDirection, ComplianceResult, ComplianceRule
from app.core.config import load_rules


class TestComplianceEngine:
    """Test the compliance engine with weighted rules and penalties"""

    def test_engine_initialization(self, mock_rules):
        """Test engine initializes with rules"""
        engine = ComplianceEngine(mock_rules)
        assert len(engine.rules) > 0

    def test_perfect_compliance(self, mock_rules, sample_room_directions):
        """Test perfect compliance scenario"""
        # Create rules that match all room directions
        perfect_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.SW, Direction.W],  # SW matches
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="kitchen",
                preferred_directions=[Direction.SE, Direction.S],  # SE matches
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="toilet",
                preferred_directions=[Direction.NW, Direction.W],  # NW matches
                weight=1.0,
                penalty=0.0
            )
        ]
        
        engine = ComplianceEngine(perfect_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        assert result.total_compliance_percentage == 100.0
        assert len(result.rule_wise_breakdown) == 3
        for rr in result.rule_wise_breakdown:
            assert rr.final_score == 1.0
            assert rr.compliance_level == 1.0

    def test_zero_compliance(self, mock_rules, sample_room_directions):
        """Test zero compliance scenario"""
        # Create rules that don't match any room directions
        zero_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.S, Direction.W],
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="kitchen",
                preferred_directions=[Direction.N, Direction.NE],
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="toilet",
                preferred_directions=[Direction.E, Direction.SE],
                weight=1.0,
                penalty=0.0
            )
        ]
        
        engine = ComplianceEngine(zero_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        assert result.total_compliance_percentage == 0.0
        assert len(result.rule_wise_breakdown) == 3
        for rr in result.rule_wise_breakdown:
            assert rr.final_score == 0.0
            assert rr.compliance_level == 0.0

    def test_partial_compliance(self, mock_rules, sample_room_directions):
        """Test partial compliance with mixed results"""
        partial_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.SW, Direction.W],  # SW matches
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="kitchen",
                preferred_directions=[Direction.N, Direction.E],  # Neither matches (SE)
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="toilet",
                preferred_directions=[Direction.NW, Direction.W],  # NW matches
                weight=1.0,
                penalty=0.0
            )
        ]
        
        engine = ComplianceEngine(partial_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        assert 0.0 < result.total_compliance_percentage < 100.0
        assert len(result.rule_wise_breakdown) == 3
        
        # Check individual scores
        bedroom_result = next(rr for rr in result.rule_wise_breakdown if rr.rule_name == "Bedroom Direction Rule")
        kitchen_result = next(rr for rr in result.rule_wise_breakdown if rr.rule_name == "Kitchen Direction Rule")
        toilet_result = next(rr for rr in result.rule_wise_breakdown if rr.rule_name == "Toilet Direction Rule")
        
        assert bedroom_result.final_score == 1.0
        assert kitchen_result.final_score == 0.0
        assert toilet_result.final_score == 1.0

    def test_weighted_compliance(self, mock_rules, sample_room_directions):
        """Test weighted compliance calculation"""
        weighted_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.SW],  # Matches
                weight=0.5,
                penalty=0.0
            ),
            ComplianceRule(
                room="kitchen",
                preferred_directions=[Direction.SE],  # Matches
                weight=0.3,
                penalty=0.0
            ),
            ComplianceRule(
                room="toilet",
                preferred_directions=[Direction.E],  # Doesn't match
                weight=0.2,
                penalty=0.0
            )
        ]
        
        engine = ComplianceEngine(weighted_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        # Expected: (0.5*1 + 0.3*1 + 0.2*0) / (0.5+0.3+0.2) = 0.8/1.0 = 0.8 -> 80%
        expected_score = 80.0
        assert abs(result.total_compliance_percentage - expected_score) < 0.001

    def test_penalty_application(self, mock_rules, sample_room_directions):
        """Test penalty application for non-compliant rooms"""
        penalty_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.SW],  # Matches
                weight=1.0,
                penalty=0.0
            ),
            ComplianceRule(
                room="kitchen",
                preferred_directions=[Direction.N],  # Doesn't match
                weight=1.0,
                penalty=0.5  # 50% penalty
            ),
            ComplianceRule(
                room="toilet",
                preferred_directions=[Direction.NW],  # Matches
                weight=1.0,
                penalty=0.0
            )
        ]
        
        engine = ComplianceEngine(penalty_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        # Bedroom: 1.0, Kitchen: 0.5 (penalty), Toilet: 1.0
        # Overall: (1.0 + 0.5 + 1.0) / 3 = 0.833... -> 83.33%
        expected_score = (1.0 + 0.5 + 1.0) / 3 * 100
        assert abs(result.total_compliance_percentage - expected_score) < 0.001

    def test_empty_room_directions(self, mock_rules):
        """Test compliance with no room directions"""
        engine = ComplianceEngine(mock_rules)
        result = engine.evaluate_compliance([])
        
        assert result.total_compliance_percentage == 0.0
        assert len(result.rule_wise_breakdown) == 0

    def test_missing_room_rules(self, sample_room_directions):
        """Test compliance when some rooms have no rules"""
        limited_rules = [
            ComplianceRule(
                room="bedroom",
                preferred_directions=[Direction.N],
                weight=1.0,
                penalty=0.0
            )
            # No rules for kitchen and toilet
        ]
        
        engine = ComplianceEngine(limited_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        assert len(result.rule_wise_breakdown) == 1  # Only bedroom
        assert result.rule_wise_breakdown[0].rule_name == "Bedroom Direction Rule"
        assert result.total_compliance_percentage == 0.0  # Bedroom doesn't match N

    def test_deterministic_evaluation(self, mock_rules, sample_room_directions):
        """Test that evaluation is deterministic"""
        engine = ComplianceEngine(mock_rules)
        result1 = engine.evaluate_compliance(sample_room_directions)
        result2 = engine.evaluate_compliance(sample_room_directions)
        
        assert result1 == result2

    def test_rule_validation(self):
        """Test rule validation during initialization"""
        # Valid rules should work
        valid_rules = [
            ComplianceRule(
                room="test",
                preferred_directions=[Direction.N],
                weight=0.5,
                penalty=0.0
            )
        ]
        engine = ComplianceEngine(valid_rules)
        assert len(engine.rules) == 1

    def test_compliance_result_structure(self, mock_rules, sample_room_directions):
        """Test that compliance results have correct structure"""
        engine = ComplianceEngine(mock_rules)
        result = engine.evaluate_compliance(sample_room_directions)
        
        assert isinstance(result, ComplianceResult)
        assert isinstance(result.total_compliance_percentage, float)
        assert 0.0 <= result.total_compliance_percentage <= 100.0
        assert isinstance(result.rule_wise_breakdown, list)
        assert isinstance(result.summary_explanation, str)
        
        for rr in result.rule_wise_breakdown:
            assert hasattr(rr, 'rule_id')
            assert hasattr(rr, 'rule_name')
            assert hasattr(rr, 'expected_direction')
            assert hasattr(rr, 'detected_direction')
            assert hasattr(rr, 'compliance_level')
            assert hasattr(rr, 'final_score')
            assert hasattr(rr, 'reasoning')
            assert isinstance(rr.final_score, float)
            assert 0.0 <= rr.final_score <= 1.0
            assert isinstance(rr.compliance_level, float)
            assert 0.0 <= rr.compliance_level <= 1.0
# Reviewed
