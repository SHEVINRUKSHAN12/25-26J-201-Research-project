from typing import List, Dict, Any
from app.schemas import (
    OrientationExplanation, RoomClassificationExplanation, 
    ComplianceRuleExplanation, ExplainabilityResult,
    Compass, RoomDetection, RuleResult, ComplianceResult, RoomComplianceResult
)
from app.core.config import YOLOConfig


class ExplainabilityService:
    """Service for generating human-readable explanations of compliance decisions"""

    def generate_explanation(self, compliance_result: ComplianceResult) -> str:
        """Generate a comprehensive explanation for the compliance result"""
        if not compliance_result.rule_wise_breakdown:
            return "No rooms detected in the floor plan for compliance analysis."

        compliant_rules = [r for r in compliance_result.rule_wise_breakdown if r.compliance_level == 1.0]
        non_compliant_rules = [r for r in compliance_result.rule_wise_breakdown if r.compliance_level == 0.0]

        explanation_parts = []

        # Overall score
        score_percent = compliance_result.total_compliance_percentage
        if score_percent == 100.0:
            explanation_parts.append(f"Perfect compliance achieved with {score_percent:.1f}% score!")
        elif score_percent >= 80.0:
            explanation_parts.append(f"Excellent compliance with {score_percent:.1f}% score.")
        elif score_percent >= 60.0:
            explanation_parts.append(f"Good compliance with {score_percent:.1f}% score.")
        elif score_percent >= 40.0:
            explanation_parts.append(f"Moderate compliance with {score_percent:.1f}% score.")
        else:
            explanation_parts.append(f"Poor compliance with only {score_percent:.1f}% score.")

        # Room details
        if compliant_rules:
            compliant_names = [r.rule_name.replace(" Direction Rule", "") for r in compliant_rules]
            explanation_parts.append(f"Compliant rooms: {', '.join(compliant_names)}")

        if non_compliant_rules:
            explanation_parts.append("Non-compliant rooms requiring attention:")
            for rule in non_compliant_rules:
                room_name = rule.rule_name.replace(" Direction Rule", "")
                explanation_parts.append(f"- {room_name} (currently facing {rule.detected_direction})")

        return " ".join(explanation_parts)

    def _explain_room_compliance(self, room_result: RoomComplianceResult) -> str:
        """Generate explanation for a single room's compliance"""
        # Map direction enum values to full names
        direction_names = {
            "N": "north",
            "NE": "northeast", 
            "E": "east",
            "SE": "southeast",
            "S": "south",
            "SW": "southwest",
            "W": "west",
            "NW": "northwest"
        }
        direction_name = direction_names.get(room_result.direction.value, room_result.direction.value.lower())
        
        if room_result.is_compliant:
            return f"{room_result.room} is excellently positioned facing {direction_name} as recommended by Vastu principles."
        else:
            return f"{room_result.room} is not in the recommended position. Currently facing {direction_name}."

    def _interpret_score(self, score: float) -> str:
        """Interpret a compliance score into human-readable terms"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.75:
            return "good"
        elif score >= 0.6:
            return "moderate"
        elif score >= 0.4:
            return "poor"
        else:
            return "very poor"

    def _generate_recommendation(self, room_result: RoomComplianceResult) -> str:
        """Generate a recommendation for non-compliant rooms"""
        return f"Consider repositioning the {room_result.room} to face {room_result.rule_applied}"


def generate_explanations(
    compass: Compass,
    raw_yolo_detections: List[Dict[str, Any]],
    processed_detections: List[RoomDetection],
    confidence_threshold: float,
    rule_results: List[RuleResult],
    total_score: float
) -> ExplainabilityResult:
    """
    Generate comprehensive explanations for all decisions in the analysis pipeline.
    
    Args:
        compass: Compass orientation data
        raw_yolo_detections: Original YOLO detections
        processed_detections: Filtered and normalized detections
        confidence_threshold: Confidence threshold used
        rule_results: Results from compliance evaluation
        total_score: Final compliance score
        
    Returns:
        Complete explainability result
    """
    orientation_exp = explain_orientation(compass)
    room_exps = explain_room_classifications(raw_yolo_detections, processed_detections, confidence_threshold, YOLOConfig().class_mapping)
    compliance_exps = explain_compliance_rules(rule_results)
    summary = generate_overall_summary(
        orientation_exp, room_exps, compliance_exps, total_score, 
        len(raw_yolo_detections), len(processed_detections)
    )
    
    return ExplainabilityResult(
        orientation_explanation=orientation_exp,
        room_classification_explanations=room_exps,
        compliance_rule_explanations=compliance_exps,
        overall_summary=summary
    )


def explain_orientation(compass: Compass) -> OrientationExplanation:
    """
    Explain how the North orientation was determined.
    """
    method = "manual_compass"  # Since we have rotation_angle from user input
    description = (
        f"North direction was set manually with a {compass.rotation_angle:.1f}-degree "
        f"clockwise rotation from the image's upward direction. This rotation affects all room "
        f"direction calculations by transforming coordinates before angle computation."
    )
    
    return OrientationExplanation(
        method=method,
        rotation_angle=compass.rotation_angle,
        description=description
    )


def explain_room_classifications(
    raw_detections: List[Dict[str, Any]], 
    processed_detections: List[RoomDetection],
    threshold: float,
    class_mapping: Dict[str, int] = None
) -> List[RoomClassificationExplanation]:
    """
    Explain the classification decisions for each room detection.
    """
    explanations = []
    
    # Create lookup for processed detections
    processed_lookup = {(det.label, tuple(det.bbox)): det for det in processed_detections}
    
    for raw_det in raw_detections:
        bbox = tuple(raw_det['bbox'])
        class_id = raw_det.get('class_id', -1)
        confidence = raw_det.get('confidence', 0.0)
        
        # Map class_id to class_name
        class_name = 'unknown'
        if class_mapping:
            for name, cid in class_mapping.items():
                if cid == class_id:
                    class_name = name
                    break
        
        # Check if this detection was accepted
        accepted = False
        processed_det = None
        for label, det in processed_lookup.items():
            if _bboxes_match(bbox, det.bbox):
                processed_det = det
                accepted = True
                break
        
        if accepted and processed_det:
            status = "accepted"
            reasoning = (
                f"Detection confidence of {confidence:.2f} exceeds the threshold of {threshold:.1f}. "
                f"Room class '{class_name}' was normalized to '{processed_det.label}' and accepted."
            )
            room_type = processed_det.label
        else:
            status = "rejected"
            if confidence < threshold:
                reasoning = (
                    f"Detection confidence of {confidence:.2f} is below the threshold of {threshold:.1f}. "
                    f"Detection was filtered out."
                )
            else:
                reasoning = (
                    f"Room class '{class_name}' is not recognized. Detection was rejected."
                )
            room_type = class_name
        
        explanations.append(RoomClassificationExplanation(
            room_type=room_type,
            confidence=confidence,
            bbox=list(bbox),
            status=status,
            reasoning=reasoning
        ))
    
    return explanations


def explain_compliance_rules(rule_results: List[RuleResult]) -> List[ComplianceRuleExplanation]:
    """
    Explain the evaluation of each compliance rule.
    """
    explanations = []
    
    for rule in rule_results:
        # Parse expected and detected from reasoning or fields
        expected = rule.expected_direction
        detected = rule.detected_direction
        
        compliance = rule.compliance_level
        penalty = rule.penalty_applied
        final_score = rule.final_score
        
        if final_score > 0:
            impact = f"+{final_score:.3f} to total score"
        else:
            impact = f"{final_score:.3f} from total score"
        
        # Enhanced reasoning
        compliance_desc = "fully compliant" if compliance == 1.0 else "partially compliant" if compliance > 0 else "non-compliant"
        reasoning = (
            f"{rule.rule_name} expected {expected}. Detected {detected}. "
            f"Compliance level is {compliance:.1f} ({compliance_desc}). "
        )
        if penalty > 0:
            reasoning += f"Penalty of {penalty:.3f} was applied due to {'partial' if compliance > 0 else 'non'}-compliance."
        else:
            reasoning += "No penalty applied."
        
        explanations.append(ComplianceRuleExplanation(
            rule_name=rule.rule_name,
            expected_condition=expected,
            detected_condition=detected,
            compliance_level=compliance,
            penalty_applied=penalty,
            score_impact=impact,
            reasoning=reasoning
        ))
    
    return explanations


def generate_overall_summary(
    orientation: OrientationExplanation,
    rooms: List[RoomClassificationExplanation],
    compliance: List[ComplianceRuleExplanation],
    total_score: float,
    raw_count: int,
    processed_count: int
) -> str:
    """
    Generate a comprehensive plain English summary.
    """
    accepted_rooms = [r for r in rooms if r.status == "accepted"]
    rejected_rooms = [r for r in rooms if r.status == "rejected"]
    
    summary = (
        f"The floor plan analysis used {orientation.method.replace('_', ' ')} orientation "
        f"with {orientation.rotation_angle:.1f}-degree rotation. "
        f"{processed_count} out of {raw_count} room detections were accepted based on "
        f"confidence threshold filtering. "
    )
    
    if rejected_rooms:
        summary += f"{len(rejected_rooms)} detections were rejected due to low confidence or unrecognized classes. "
    
    summary += (
        f"Compliance evaluation applied {len(compliance)} rules with weighted scoring. "
        f"Total compliance score is {total_score:.1f}%, "
    )
    
    critical_violations = [c for c in compliance if c.compliance_level == 0.0 and "entrance" in c.rule_name.lower()]
    if critical_violations:
        summary += "reduced by penalties for critical violations in entrance placement."
    else:
        summary += "with penalties applied for any rule violations."
    
    return summary


def _bboxes_match(bbox1: tuple, bbox2: List[float], tolerance: float = 1.0) -> bool:
    """
    Check if two bounding boxes match within tolerance.
    """
    if len(bbox1) != len(bbox2):
        return False
    
    for a, b in zip(bbox1, bbox2):
        if abs(a - b) > tolerance:
            return False
    
    return True
# Reviewed
