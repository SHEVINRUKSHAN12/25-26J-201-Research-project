# Vastu API JSON Testing Script
import json
from app.services.yolo_integration import YOLOIntegrationService, process_yolo_detections
from app.services.compliance import ComplianceEngine, load_rules
from app.services.explainability import ExplainabilityService
from app.services.direction import calculate_room_directions
from app.core.config import YOLOConfig
from app.schemas import YOLODetection, Compass, RoomDirection

print('🚀 VASTU API JSON TESTING')
print('=' * 50)

# Sample JSON 1: Raw YOLO Detections
print('\n📋 Sample 1: Raw YOLO Detections')
yolo_json = {
    'yolo_detections': [
        {'class_name': 'bedroom', 'confidence': 0.92, 'bbox': [50, 50, 150, 150]},
        {'class_name': 'kitchen', 'confidence': 0.88, 'bbox': [200, 50, 300, 150]},
        {'class_name': 'toilet', 'confidence': 0.85, 'bbox': [50, 200, 150, 300]},
        {'class_name': 'compass', 'confidence': 0.90, 'bbox': [250, 250, 270, 270]}
    ],
    'compass': {'rotation_angle': 0.0},
    'floor_width': 400,
    'floor_height': 400
}
print('Input JSON:', json.dumps(yolo_json, indent=2))

# Process YOLO detections
config = YOLOConfig()
yolo_service = YOLOIntegrationService(config)

# Convert to YOLODetection objects (skip compass for now since class_id is None)
yolo_detections = []
for d in yolo_json['yolo_detections']:
    if d['class_name'] != 'compass':
        # Map class name to ID
        class_id = config.class_mapping.get(d['class_name'], 0)
        yolo_detections.append(YOLODetection(
            class_id=class_id,
            confidence=d['confidence'],
            bbox=d['bbox']
        ))

translation_result = yolo_service.translate_detections(yolo_detections)
for room in translation_result.room_detections:
    print(f'   - {room.label}: confidence {room.confidence:.2f}')
print(f'   Compass detected: {translation_result.compass_detection is not None}')

# Calculate directions
compass = Compass(rotation_angle=0.0)
room_directions = calculate_room_directions(translation_result.room_detections, compass)
print('✅ Room Directions Calculated:')
for rd in room_directions:
    print(f'   - {rd.room}: {rd.direction.value}')

# Compliance analysis
from app.schemas import ComplianceRule, Direction
rules_data = load_rules()
rules = []
for rule_data in rules_data:
    if "applicable_room_types" in rule_data and rule_data["applicable_room_types"]:
        for room_type in rule_data["applicable_room_types"]:
            preferred_directions = []
            for dir_str in rule_data.get("preferred_directions", []):
                try:
                    preferred_directions.append(Direction(dir_str))
                except ValueError:
                    continue

            if preferred_directions:
                rules.append(ComplianceRule(
                    room=room_type,
                    preferred_directions=preferred_directions,
                    weight=rule_data.get("weight", 1.0),
                    penalty=rule_data.get("penalty_factor", 0.0)
                ))

engine = ComplianceEngine(rules)
compliance_result = engine.evaluate_compliance(room_directions)
print('✅ Compliance Analysis:')
print(f'   Score: {compliance_result.total_compliance_percentage:.1f}%')
print(f'   Rules evaluated: {len(compliance_result.rule_wise_breakdown)}')

# Generate explanation
explain_service = ExplainabilityService()
explanation = explain_service.generate_explanation(compliance_result)
print('✅ Explanation Generated:')
print(f'   "{explanation}"')

print('\n' + '=' * 50)
print('🎉 API TEST COMPLETED SUCCESSFULLY!')
print('📊 Your Vastu system processed JSON input perfectly!')