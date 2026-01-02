import pytest
from app.services.yolo_integration import YOLOIntegrationService
from app.schemas import YOLODetection, RoomDetection, CompassDetection
from app.core.config import YOLOConfig


class TestYOLOIntegrationService:
    """Test the YOLO integration service for safe ML output translation"""

    def test_service_initialization(self):
        """Test service initializes with config"""
        config = YOLOConfig(
            confidence_threshold=0.5,
            max_detections=100,
            class_mapping={"bedroom": 0, "kitchen": 1, "toilet": 2}
        )
        service = YOLOIntegrationService(config)
        assert service.config.confidence_threshold == 0.5
        assert service.config.max_detections == 100

    def test_empty_yolo_detections(self):
        """Test processing empty YOLO detections"""
        config = YOLOConfig()
        service = YOLOIntegrationService(config)
        
        result = service.translate_detections([])
        assert result.room_detections == []
        assert result.compass_detection is None

    def test_room_detection_translation(self):
        """Test translation of room detections"""
        config = YOLOConfig(
            confidence_threshold=0.5,
            class_mapping={"bedroom": 0, "kitchen": 1, "toilet": 2}
        )
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(
                class_id=0,  # bedroom
                confidence=0.9,
                bbox=[10, 20, 30, 40]
            ),
            YOLODetection(
                class_id=1,  # kitchen
                confidence=0.8,
                bbox=[50, 60, 70, 80]
            ),
            YOLODetection(
                class_id=2,  # toilet
                confidence=0.3,  # Below threshold
                bbox=[90, 100, 110, 120]
            )
        ]
        
        result = service.translate_detections(yolo_detections)
        
        assert len(result.room_detections) == 2  # Toilet filtered out
        assert result.room_detections[0].label == "bedroom"
        assert result.room_detections[0].confidence == 0.9
        assert result.room_detections[0].bbox == [10, 20, 30, 40]
        assert result.room_detections[1].label == "kitchen"
        assert result.room_detections[1].confidence == 0.8

    def test_compass_detection_translation(self):
        """Test translation of compass detection"""
        config = YOLOConfig(
            compass_class_id=10,
            confidence_threshold=0.7
        )
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(
                class_id=10,  # compass
                confidence=0.85,
                bbox=[100, 200, 150, 250]
            )
        ]
        
        result = service.translate_detections(yolo_detections)
        
        assert result.compass_detection is not None
        assert result.compass_detection.confidence == 0.85
        assert result.compass_detection.bbox == [100, 200, 150, 250]

    def test_compass_rotation_calculation(self):
        """Test compass rotation angle calculation"""
        config = YOLOConfig(compass_class_id=10)
        service = YOLOIntegrationService(config)
        
        # Test with compass at different positions
        # Assuming compass center calculation and rotation logic
        compass_detection = CompassDetection(
            confidence=0.9,
            bbox=[90, 190, 110, 210]  # Center at (100, 200)
        )
        
        # Mock floor center at (100, 200) - should result in 0 rotation
        rotation_angle = service._calculate_compass_rotation(compass_detection, (100, 200))
        assert rotation_angle == 0.0

    def test_confidence_filtering(self):
        """Test that low confidence detections are filtered"""
        config = YOLOConfig(confidence_threshold=0.8)
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[0, 0, 10, 10]),  # Pass
            YOLODetection(class_id=1, confidence=0.7, bbox=[10, 10, 20, 20]),  # Fail
            YOLODetection(class_id=2, confidence=0.85, bbox=[20, 20, 30, 30])  # Pass
        ]
        
        result = service.translate_detections(yolo_detections)
        assert len(result.room_detections) == 2
        confidences = [rd.confidence for rd in result.room_detections]
        assert all(c >= 0.8 for c in confidences)

    def test_max_detections_limit(self):
        """Test that detections are limited by max_detections"""
        config = YOLOConfig(max_detections=2)
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[0, 0, 10, 10]),
            YOLODetection(class_id=1, confidence=0.8, bbox=[10, 10, 20, 20]),
            YOLODetection(class_id=2, confidence=0.7, bbox=[20, 20, 30, 30])  # Should be limited
        ]
        
        result = service.translate_detections(yolo_detections)
        assert len(result.room_detections) <= 2

    def test_unknown_class_handling(self):
        """Test handling of unknown class IDs"""
        config = YOLOConfig(class_mapping={"bedroom": 0, "kitchen": 1})
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[0, 0, 10, 10]),  # Known
            YOLODetection(class_id=99, confidence=0.8, bbox=[10, 10, 20, 20])  # Unknown
        ]
        
        result = service.translate_detections(yolo_detections)
        assert len(result.room_detections) == 1  # Only known class
        assert result.room_detections[0].label == "bedroom"

    def test_bbox_validation(self):
        """Test that invalid bboxes are handled"""
        config = YOLOConfig()
        service = YOLOIntegrationService(config)
        
        # Test with invalid bbox (negative coordinates)
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[-10, -10, 10, 10])
        ]
        
        result = service.translate_detections(yolo_detections)
        # Should still process but bbox remains as-is (validation happens elsewhere)
        assert len(result.room_detections) == 1

    def test_compass_priority(self):
        """Test that highest confidence compass is selected"""
        config = YOLOConfig(compass_class_id=10)
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=10, confidence=0.7, bbox=[0, 0, 10, 10]),
            YOLODetection(class_id=10, confidence=0.9, bbox=[20, 20, 30, 30]),  # Higher confidence
            YOLODetection(class_id=10, confidence=0.6, bbox=[40, 40, 50, 50])
        ]
        
        result = service.translate_detections(yolo_detections)
        assert result.compass_detection.confidence == 0.9
        assert result.compass_detection.bbox == [20, 20, 30, 30]

    def test_deterministic_translation(self):
        """Test that translation is deterministic"""
        config = YOLOConfig(class_mapping={"bedroom": 0})
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[10, 20, 30, 40])
        ]
        
        result1 = service.translate_detections(yolo_detections)
        result2 = service.translate_detections(yolo_detections)
        
        assert result1 == result2

    def test_mixed_detection_types(self):
        """Test processing mixed room and compass detections"""
        config = YOLOConfig(
            class_mapping={"bedroom": 0, "kitchen": 1},
            compass_class_id=10
        )
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[0, 0, 10, 10]),  # bedroom
            YOLODetection(class_id=10, confidence=0.8, bbox=[50, 50, 60, 60]),  # compass
            YOLODetection(class_id=1, confidence=0.7, bbox=[20, 20, 30, 30])  # kitchen
        ]
        
        result = service.translate_detections(yolo_detections)
        
        assert len(result.room_detections) == 2
        assert result.compass_detection is not None
        assert result.compass_detection.confidence == 0.8

    def test_service_config_validation(self):
        """Test that service validates configuration"""
        # Should not raise exception with valid config
        config = YOLOConfig()
        service = YOLOIntegrationService(config)
        assert service is not None

    def test_empty_class_mapping(self):
        """Test behavior with empty class mapping"""
        config = YOLOConfig(class_mapping={})
        service = YOLOIntegrationService(config)
        
        yolo_detections = [
            YOLODetection(class_id=0, confidence=0.9, bbox=[0, 0, 10, 10])
        ]
        
        result = service.translate_detections(yolo_detections)
        # Should not translate unknown classes
        assert len(result.room_detections) == 0
# Reviewed
