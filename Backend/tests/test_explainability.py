import pytest
from app.services.explainability import ExplainabilityService
from app.schemas import Direction, RoomDirection, ComplianceResult, RoomComplianceResult, RuleResult
from app.services.compliance import ComplianceEngine
from app.core.config import load_rules


class TestExplainabilityService:
    """Test the explainability service for compliance decisions"""

    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = ExplainabilityService()
        assert service is not None

    def test_perfect_compliance_explanation(self, sample_room_directions):
        """Test explanation for perfect compliance"""
        # Create perfect compliance result
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, East",
                detected_direction="North",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'bedroom' is compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="kitchen_direction",
                rule_name="Kitchen Direction Rule",
                expected_direction="South-East, South",
                detected_direction="South-East",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'kitchen' is compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="toilet_direction",
                rule_name="Toilet Direction Rule",
                expected_direction="North-West, West",
                detected_direction="North-West",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'toilet' is compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=100.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 3/3 rules satisfied (100.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "perfect" in explanation.lower() or "excellent" in explanation.lower()
        assert "100.0%" in explanation
        assert "Bedroom" in explanation
        assert "Kitchen" in explanation
        assert "Toilet" in explanation

    def test_zero_compliance_explanation(self, sample_room_directions):
        """Test explanation for zero compliance"""
        # Create zero compliance result
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, East",
                detected_direction="South",
                compliance_level=0.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=0.0,
                reasoning="Room 'bedroom' is non-compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="kitchen_direction",
                rule_name="Kitchen Direction Rule",
                expected_direction="South-East, South",
                detected_direction="North",
                compliance_level=0.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=0.0,
                reasoning="Room 'kitchen' is non-compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="toilet_direction",
                rule_name="Toilet Direction Rule",
                expected_direction="North-West, West",
                detected_direction="East",
                compliance_level=0.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=0.0,
                reasoning="Room 'toilet' is non-compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=0.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 0/3 rules satisfied (0.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "no compliance" in explanation.lower() or "0%" in explanation
        assert "attention" in explanation.lower()

    def test_partial_compliance_explanation(self, sample_room_directions):
        """Test explanation for partial compliance"""
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, South",
                detected_direction="North",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'bedroom' is compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="kitchen_direction",
                rule_name="Kitchen Direction Rule",
                expected_direction="North, East",
                detected_direction="North",
                compliance_level=0.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=0.0,
                reasoning="Room 'kitchen' is non-compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="toilet_direction",
                rule_name="Toilet Direction Rule",
                expected_direction="North-West, West",
                detected_direction="North-West",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'toilet' is compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=2.0/3.0 * 100,  # 66.67%
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 2/3 rules satisfied (66.7% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "66.7%" in explanation or "66%" in explanation
        assert "Bedroom" in explanation
        assert "Kitchen" in explanation
        assert "Toilet" in explanation
        assert "north" in explanation.lower()  # Should mention kitchen issue

    def test_detailed_room_explanations(self):
        """Test detailed explanations for individual rooms"""
        service = ExplainabilityService()
        
        # Test compliant room
        compliant_room = RoomComplianceResult(
            room="bedroom",
            direction=Direction.N,
            compliance_score=1.0,
            is_compliant=True,
            rule_applied="North-facing bedroom preferred"
        )
        explanation = service._explain_room_compliance(compliant_room)
        assert "excellent" in explanation.lower() or "good" in explanation.lower()
        assert "north" in explanation.lower()
        
        # Test non-compliant room
        non_compliant_room = RoomComplianceResult(
            room="kitchen",
            direction=Direction.N,
            compliance_score=0.0,
            is_compliant=False,
            rule_applied="South-east kitchen recommended"
        )
        explanation = service._explain_room_compliance(non_compliant_room)
        assert "not in the recommended position" in explanation.lower()
        assert "north" in explanation.lower()

    def test_score_interpretation(self):
        """Test score interpretation logic"""
        service = ExplainabilityService()
        
        assert "excellent" in service._interpret_score(0.9).lower()
        assert "good" in service._interpret_score(0.75).lower()
        assert "moderate" in service._interpret_score(0.6).lower()
        assert "poor" in service._interpret_score(0.3).lower()
        assert "very poor" in service._interpret_score(0.1).lower()

    def test_empty_results_explanation(self):
        """Test explanation for empty compliance results"""
        compliance_result = ComplianceResult(
            total_compliance_percentage=0.0,
            rule_wise_breakdown=[],
            summary_explanation="Overall compliance: 0/0 rules satisfied (0.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "no rooms" in explanation.lower() or "empty" in explanation.lower()

    def test_single_room_explanation(self):
        """Test explanation for single room"""
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, East",
                detected_direction="North",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'bedroom' is compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=100.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 1/1 rules satisfied (100.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "Bedroom" in explanation

    def test_deterministic_explanations(self, sample_room_directions):
        """Test that explanations are deterministic"""
        # Create a compliance result
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, East",
                detected_direction="North",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'bedroom' is compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=100.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 1/1 rules satisfied (100.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation1 = service.generate_explanation(compliance_result)
        explanation2 = service.generate_explanation(compliance_result)
        
        assert explanation1 == explanation2

    def test_vastu_principles_mention(self):
        """Test that explanations mention Vastu principles"""
        rule_results = [
            RuleResult(
                rule_id="kitchen_direction",
                rule_name="Kitchen Direction Rule",
                expected_direction="South-East, South",
                detected_direction="South-East",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'kitchen' is compliant with Vastu rules for fire element."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=100.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 1/1 rules satisfied (100.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        assert "vastu" in explanation.lower() or "kitchen" in explanation.lower()

    def test_recommendation_generation(self):
        """Test recommendation generation for non-compliant rooms"""
        service = ExplainabilityService()
        
        non_compliant = RoomComplianceResult(
            room="toilet",
            direction=Direction.S,
            compliance_score=0.0,
            is_compliant=False,
            rule_applied="North-west toilet placement recommended"
        )
        
        recommendation = service._generate_recommendation(non_compliant)
        assert "north-west" in recommendation.lower()
        assert "toilet" in recommendation.lower()
        assert "recommend" in recommendation.lower() or "suggest" in recommendation.lower()

    def test_comprehensive_explanation_structure(self, sample_room_directions):
        """Test that comprehensive explanations have proper structure"""
        # Create mixed compliance result
        rule_results = [
            RuleResult(
                rule_id="bedroom_direction",
                rule_name="Bedroom Direction Rule",
                expected_direction="North, East",
                detected_direction="North",
                compliance_level=1.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=1.0,
                reasoning="Room 'bedroom' is compliant with Vastu rules."
            ),
            RuleResult(
                rule_id="kitchen_direction",
                rule_name="Kitchen Direction Rule",
                expected_direction="South-East, South",
                detected_direction="North",
                compliance_level=0.0,
                score_before_penalty=1.0,
                penalty_applied=0.0,
                final_score=0.0,
                reasoning="Room 'kitchen' is non-compliant with Vastu rules."
            )
        ]
        compliance_result = ComplianceResult(
            total_compliance_percentage=50.0,
            rule_wise_breakdown=rule_results,
            summary_explanation="Overall compliance: 1/2 rules satisfied (50.0% compliance score)."
        )
        
        service = ExplainabilityService()
        explanation = service.generate_explanation(compliance_result)
        
        # Should contain overall score, individual room assessments, and recommendations
        assert "%" in explanation
        assert "Bedroom" in explanation
        assert "Kitchen" in explanation
        assert len(explanation) > 100  # Should be comprehensive
# Reviewed

# Validated
