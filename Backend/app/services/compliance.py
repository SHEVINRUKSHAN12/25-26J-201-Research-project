import json
import os
from typing import List, Dict, Any, Tuple
from app.schemas import RoomDirection, Direction, RuleResult, ComplianceResult, ComplianceRule, RoomComplianceResult


class ComplianceEngine:
    """Engine for evaluating Vastu compliance with weighted rules and penalties"""

    def __init__(self, rules: List[ComplianceRule]):
        self.rules = rules

    def evaluate_compliance(self, room_directions: List[RoomDirection]) -> ComplianceResult:
        """Evaluate compliance and return detailed results"""
        rule_results = []
        evaluated_rules = []  # Track which rules were actually evaluated
        
        for rule in self.rules:
            # Find matching room direction
            matching_room = next((rd for rd in room_directions if rd.room == rule.room), None)
            if matching_room:
                is_compliant = matching_room.direction in rule.preferred_directions
                compliance_level = 1.0 if is_compliant else 0.0
                score_before_penalty = 1.0
                penalty_applied = rule.penalty if not is_compliant else 0.0
                if not is_compliant:
                    if penalty_applied == 0.0:
                        final_score = 0.0
                    elif penalty_applied > 1.0:
                        final_score = 1.0 / penalty_applied
                    else:
                        final_score = 1.0 - penalty_applied
                else:
                    final_score = 1.0
                
                expected_direction = ", ".join([d.value for d in rule.preferred_directions])
                detected_direction = matching_room.direction.value
                
                reasoning = f"Room '{rule.room}' is {'compliant' if is_compliant else 'non-compliant'} with Vastu rules. " \
                           f"Expected: {expected_direction}, Detected: {detected_direction}."
                if not is_compliant:
                    reasoning += f" Penalty of {rule.penalty} applied."
                
                rule_results.append(RuleResult(
                    rule_id=f"{rule.room}_direction",
                    rule_name=f"{rule.room.capitalize()} Direction Rule",
                    expected_direction=expected_direction,
                    detected_direction=detected_direction,
                    compliance_level=compliance_level,
                    score_before_penalty=score_before_penalty,
                    penalty_applied=penalty_applied,
                    final_score=final_score,
                    reasoning=reasoning
                ))
                evaluated_rules.append(rule)
        
        # Calculate total compliance percentage using weighted average
        if rule_results:
            weighted_sum = sum(rr.final_score * rule.weight for rr, rule in zip(rule_results, evaluated_rules))
            total_weight = sum(rule.weight for rule in evaluated_rules)
            total_compliance_percentage = (weighted_sum / total_weight) * 100.0 if total_weight > 0 else 0.0
            total_compliance_percentage = max(0.0, min(100.0, total_compliance_percentage))
        else:
            total_compliance_percentage = 0.0
            
        # Generate summary explanation
        compliant_count = sum(1 for rr in rule_results if rr.compliance_level == 1.0)
        total_rules = len(rule_results)
        summary_explanation = f"Overall compliance: {compliant_count}/{total_rules} rules satisfied " \
                             f"({total_compliance_percentage:.1f}% compliance score)."
        
        return ComplianceResult(
            total_compliance_percentage=total_compliance_percentage,
            rule_wise_breakdown=rule_results,
            summary_explanation=summary_explanation
        )


def load_rules() -> List[Dict[str, Any]]:
    """
    Load Vastu compliance rules from the configuration file.
    """
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'core', 'rules.json')
    with open(rules_path, 'r') as f:
        return json.load(f)


def evaluate_compliance(room_directions: List[RoomDirection]) -> ComplianceResult:
    """
    Evaluate Vastu compliance with weighted scoring, partial compliance, and penalties.
    Returns detailed breakdown and summary explanation.
    """
    rules = load_rules()
    rule_breakdown = []
    total_weight = sum(rule['weight'] for rule in rules)
    total_final_score = 0.0
    
    for rule in rules:
        result = evaluate_single_rule(rule, room_directions)
        rule_breakdown.append(result)
        total_final_score += result.final_score
    
    total_compliance_percentage = (total_final_score / total_weight) * 100 if total_weight > 0 else 0.0
    total_compliance_percentage = max(0.0, min(100.0, total_compliance_percentage))
    
    summary_explanation = generate_summary_explanation(rule_breakdown, total_compliance_percentage)
    
    return ComplianceResult(
        total_compliance_percentage=round(total_compliance_percentage, 1),
        rule_wise_breakdown=rule_breakdown,
        summary_explanation=summary_explanation
    )


def evaluate_single_rule(rule: Dict[str, Any], room_directions: List[RoomDirection]) -> RuleResult:
    """
    Evaluate a single Vastu rule and return detailed result.
    """
    rule_id = rule['rule_id']
    rule_name = rule['rule_name']
    weight = rule['weight']
    penalty_factor = rule['penalty_factor']
    partial_allowed = rule['partial_allowed']
    template = rule['explanation_template']
    
    # Determine rule type and evaluate
    if 'preferred_directions' in rule:
        compliance_level, detected_info = evaluate_preferred_rule(rule, room_directions)
    elif 'avoid_room_types' in rule:
        compliance_level, detected_info = evaluate_avoid_rule(rule, room_directions)
    else:
        compliance_level, detected_info = 0.0, {"detected": "Unknown", "expected": "Undefined"}
    
    # Calculate scores
    score_before_penalty = weight * compliance_level
    penalty_applied = penalty_factor * (1 - compliance_level) * weight
    final_score = score_before_penalty - penalty_applied
    
    # Generate reasoning
    reasoning = generate_reasoning(template, rule, compliance_level, detected_info)
    
    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        expected_direction=detected_info.get('expected', 'N/A'),
        detected_direction=detected_info.get('detected', 'N/A'),
        compliance_level=round(compliance_level, 2),
        score_before_penalty=round(score_before_penalty, 3),
        penalty_applied=round(penalty_applied, 3),
        final_score=round(final_score, 3),
        reasoning=reasoning
    )


def evaluate_preferred_rule(rule: Dict[str, Any], room_directions: List[RoomDirection]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate rules with preferred directions (e.g., kitchen in SE/E).
    """
    applicable_rooms = [rd for rd in room_directions if any(rt in rd.room.lower() for rt in rule['applicable_room_types'])]
    
    if not applicable_rooms:
        return 1.0, {"expected": ', '.join(rule['preferred_directions']), "detected": "No rooms detected"}
    
    preferred_dirs = [Direction[d] for d in rule['preferred_directions']]
    compliant_rooms = [rd for rd in applicable_rooms if rd.direction in preferred_dirs]
    
    if rule['partial_allowed']:
        compliance_level = len(compliant_rooms) / len(applicable_rooms)
    else:
        compliance_level = 1.0 if len(compliant_rooms) == len(applicable_rooms) else 0.0
    
    detected_directions = [rd.direction.value for rd in applicable_rooms]
    return compliance_level, {
        "expected": ', '.join(rule['preferred_directions']),
        "detected": ', '.join(detected_directions),
        "correct_count": len(compliant_rooms),
        "total_count": len(applicable_rooms)
    }


def evaluate_avoid_rule(rule: Dict[str, Any], room_directions: List[RoomDirection]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate rules that avoid certain room combinations (e.g., dining not with toilet).
    """
    target_rooms = [rd for rd in room_directions if rd.room.lower() == rule['applicable_room_types'][0]]
    avoid_rooms = [rd for rd in room_directions if any(rt in rd.room.lower() for rt in rule['avoid_room_types'])]
    
    if not target_rooms or not avoid_rooms:
        return 1.0, {"expected": "Separate directions", "detected": "Rooms not present"}
    
    target_dir = target_rooms[0].direction
    avoid_dirs = {rd.direction for rd in avoid_rooms}
    
    compliance_level = 1.0 if target_dir not in avoid_dirs else 0.0
    
    return compliance_level, {
        "expected": "Separate directions",
        "detected": f"Dining: {target_dir.value}, Toilets: {', '.join(d.value for d in avoid_dirs)}",
        "dining_dir": target_dir.value,
        "toilet_dirs": ', '.join(d.value for d in avoid_dirs)
    }


def generate_reasoning(template: str, rule: Dict[str, Any], compliance_level: float, detected_info: Dict[str, Any]) -> str:
    """
    Generate human-readable reasoning using the template.
    """
    compliance_desc = "fully compliant" if compliance_level == 1.0 else "partially compliant" if compliance_level > 0 else "non-compliant"
    
    # Fill template placeholders
    reasoning = template.format(
        preferred=detected_info.get('expected', 'N/A'),
        detected=detected_info.get('detected', 'N/A'),
        compliance_level=f"{compliance_level:.1f} ({compliance_desc})",
        correct_count=detected_info.get('correct_count', 'N/A'),
        total_count=detected_info.get('total_count', 'N/A'),
        dining_dir=detected_info.get('dining_dir', 'N/A'),
        toilet_dirs=detected_info.get('toilet_dirs', 'N/A')
    )
    
    # Add penalty information if applicable
    if compliance_level < 1.0:
        penalty_factor = rule['penalty_factor']
        reasoning += f" Penalty factor of {penalty_factor} applied due to {'partial' if compliance_level > 0 else 'non'}-compliance."
    
    return reasoning


def generate_summary_explanation(rule_breakdown: List[RuleResult], total_score: float) -> str:
    """
    Generate a human-readable summary of the overall compliance.
    """
    critical_violations = [r for r in rule_breakdown if r.compliance_level == 0.0 and r.rule_name in ["Main Entrance Direction", "Toilet Placement"]]
    partial_compliances = [r for r in rule_breakdown if 0 < r.compliance_level < 1.0]
    full_compliances = [r for r in rule_breakdown if r.compliance_level == 1.0]
    
    summary = f"Overall Vastu compliance is {total_score:.1f}%. "
    
    if critical_violations:
        summary += f"Critical violations in {', '.join([v.rule_name for v in critical_violations])} significantly reduced the score. "
    
    if partial_compliances:
        summary += f"Partial compliance in {', '.join([p.rule_name for p in partial_compliances])}. "
    
    if full_compliances:
        summary += f"Full compliance in {', '.join([f.rule_name for f in full_compliances])}. "
    
    return summary.strip()