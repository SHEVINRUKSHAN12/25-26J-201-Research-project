import logging
import os
from typing import List, Dict, Any, Tuple, Optional
from app.schemas import RoomDetection, YOLODetection, CompassDetection, YOLOTranslationResult
from app.core.config import YOLOConfig

try:
    from ultralytics import YOLO  # type: ignore
except ImportError:
    YOLO = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best.pt")

# Normalization mapping for room types
ROOM_NORMALIZATION = {
    # Toilet variants
    "bathroom": "toilet",
    "toilet": "toilet",
    "wc": "toilet",
    "restroom": "toilet",
    "washroom": "toilet",
    
    # Living room variants
    "living": "living",
    "lounge": "living",
    "drawing": "living",
    "living_room": "living",
    
    # Other standard rooms
    "bedroom": "bedroom",
    "kitchen": "kitchen",
    "dining": "dining",
    "entrance": "entrance",
    "main_door": "entrance",
    "hall": "living",
    "study": "study",
    "office": "study",
    "master_bedroom": "bedroom",
    "study_room": "study",
    "pooja": "living",
    "parking": "entrance",  # Optional: map to entrance or ignore
    "staircase": "living",  # Optional: ignore or map
    "store_room": "study",  # Optional: ignore or map
    "utility": "living",    # Optional: ignore or map
    
    # Add more as needed
}

# Known valid room types
VALID_ROOM_TYPES = set(ROOM_NORMALIZATION.values())


class YOLOIntegrationService:
    """Service for safely translating YOLO ML outputs to structured data"""

    def __init__(self, config: YOLOConfig):
        self.config = config
        self._model = None  # Lazy loading

    @property
    def model(self):
        """Lazy load the YOLO model"""
        if self._model is None:
            try:
                self._model = YOLO(MODEL_PATH)
                logger.info(f"Compass model loaded from: {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                raise
        return self._model

    def translate_detections(self, yolo_detections: List[YOLODetection]) -> YOLOTranslationResult:
        """Translate YOLO detections into structured room and compass detections"""
        # Filter by confidence
        filtered_detections = [
            det for det in yolo_detections 
            if det.confidence >= self.config.confidence_threshold
        ]
        
        # Limit detections
        filtered_detections = filtered_detections[:self.config.max_detections]
        
        # Separate room and compass detections
        room_dets = []
        compass_det = None
        
        for det in filtered_detections:
            if det.class_id == self.config.compass_class_id:
                # Take the highest confidence compass detection
                if compass_det is None or det.confidence > compass_det.confidence:
                    compass_det = CompassDetection(
                        confidence=det.confidence,
                        bbox=det.bbox
                    )
            else:
                # Try to map class_id to room type
                room_type = None
                for name, cid in self.config.class_mapping.items():
                    if cid == det.class_id:
                        room_type = name
                        break
                
                if room_type:
                    room_dets.append(RoomDetection(
                        label=room_type,
                        confidence=det.confidence,
                        bbox=det.bbox
                    ))
        
        return YOLOTranslationResult(
            room_detections=room_dets,
            compass_detection=compass_det
        )

    def _calculate_compass_rotation(self, compass_detection: CompassDetection, floor_center: Tuple[float, float]) -> float:
        """Calculate compass rotation angle from detection and floor center"""
        # Simple implementation: assume compass points to floor center
        compass_center_x = (compass_detection.bbox[0] + compass_detection.bbox[2]) / 2
        compass_center_y = (compass_detection.bbox[1] + compass_detection.bbox[3]) / 2
        
        # Vector from floor center to compass center
        dx = compass_center_x - floor_center[0]
        dy = compass_center_y - floor_center[1]
        
        # Calculate angle
        import math
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360


def process_yolo_detections(yolo_detections: List[Dict[str, Any]], confidence_threshold: float = 0.4) -> List[RoomDetection]:
    """
    Process raw YOLO detections into structured RoomDetection objects.

    This function implements the complete YOLO → RoomDetection pipeline:
    1. Filter detections by confidence threshold
    2. Normalize room class names to standard types (e.g., 'bathroom' → 'toilet')
    3. Validate against known room types
    4. Resolve overlapping detections using IoU-based non-maximum suppression
    5. Convert to validated RoomDetection objects with proper error handling

    Args:
        yolo_detections: List of YOLO detection dictionaries with keys:
            - 'class_name': String room type label
            - 'confidence': Float confidence score (0.0-1.0)
            - 'bbox': List of 4 floats [x, y, width, height]
        confidence_threshold: Minimum confidence score to accept detection (default: 0.4)

    Returns:
        List of validated RoomDetection objects, sorted by confidence descending.
        Invalid detections are logged and skipped.

    Raises:
        No exceptions raised; invalid inputs are logged and skipped for robustness.
    """
    if not yolo_detections:
        logger.info("No YOLO detections provided")
        return []
    
    logger.info(f"Processing {len(yolo_detections)} YOLO detections")
    
    # Step 1: Filter by confidence
    filtered_detections = []
    for det in yolo_detections:
        try:
            conf = float(det.get('confidence', 0))
            if conf >= confidence_threshold:
                filtered_detections.append(det)
            else:
                logger.debug(f"Ignored detection {det.get('class_name', 'unknown')} with confidence {conf:.2f} < {confidence_threshold}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid confidence value in detection {det}: {e}")
    
    # Step 2: Normalize class names and validate
    normalized_detections = []
    for det in filtered_detections:
        class_name = det.get('class_name', '').strip().lower()
        normalized_name = ROOM_NORMALIZATION.get(class_name)
        
        if normalized_name and normalized_name in VALID_ROOM_TYPES:
            det['normalized_class'] = normalized_name
            normalized_detections.append(det)
        else:
            logger.info(f"Rejected unknown class: '{class_name}' (normalized to: {normalized_name})")
    
    # Step 3: Handle overlapping detections deterministically
    final_detections = _resolve_overlaps(normalized_detections)
    
    # Step 4: Convert to RoomDetection objects
    room_detections = []
    for det in final_detections:
        try:
            bbox = det['bbox']
            if len(bbox) != 4:
                logger.warning(f"Invalid bbox format: {bbox}")
                continue
                
            room_detection = RoomDetection(
                label=det['normalized_class'],
                confidence=float(det['confidence']),
                bbox=[float(x) for x in bbox]
            )
            room_detections.append(room_detection)
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error creating RoomDetection from {det}: {e}")
    
    logger.info(f"Successfully processed {len(room_detections)} room detections")
    return room_detections


def _resolve_overlaps(detections: List[Dict[str, Any]], iou_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Resolve overlapping detections by keeping the highest confidence one.
    
    Args:
        detections: List of detection dictionaries, sorted by confidence descending
        iou_threshold: IoU threshold for considering boxes as overlapping
        
    Returns:
        List of non-overlapping detections
    """
    if not detections:
        return []
    
    # Sort by confidence descending
    sorted_detections = sorted(detections, key=lambda x: x.get('confidence', 0), reverse=True)
    selected = []
    
    for det in sorted_detections:
        # Check if this detection overlaps with any selected detection
        overlaps = False
        for selected_det in selected:
            if _calculate_iou(det['bbox'], selected_det['bbox']) > iou_threshold:
                overlaps = True
                logger.debug(f"Rejected overlapping detection: {det.get('normalized_class')} overlaps with {selected_det.get('normalized_class')}")
                break
        
        if not overlaps:
            selected.append(det)
    
    return selected


def _calculate_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) for two bounding boxes.
    
    Args:
        bbox1, bbox2: [x, y, w, h] format
        
    Returns:
        IoU value between 0 and 1
    """
    try:
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Convert to [x1, y1, x2, y2] format
        box1 = [x1, y1, x1 + w1, y1 + h1]
        box2 = [x2, y2, x2 + w2, y2 + h2]
        
        # Calculate intersection
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - intersection_area
        
        if union_area == 0:
            return 0.0
            
        return intersection_area / union_area
        
    except (IndexError, TypeError):
        return 0.0


def get_supported_room_types() -> List[str]:
    """
    Get list of supported room types for validation.
    """
    return sorted(list(VALID_ROOM_TYPES))
# Reviewed

# Validated
