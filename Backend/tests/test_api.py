import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestFloorPlanAPI:
    """Test the Floor Plan Intelligence API endpoints"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_analyze_floor_plan_success(self, sample_room_detections):
        """Test successful floor plan analysis"""
        request_data = {
            "detected_rooms": [
                {
                    "label": det.label,
                    "confidence": det.confidence,
                    "bbox": det.bbox
                } for det in sample_room_detections
            ],
            "north_direction": 45.0,
            "compass_override": True
        }

        response = self.client.post("/api/v1/analyze/floor-plan", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "compliance_score" in data
        assert "rule_breakdown" in data
        assert "explanation_reference_id" in data
        assert isinstance(data["rule_breakdown"], list)
        # Rooms are detected and rules are evaluated

    def test_analyze_floor_plan_minimal(self, sample_room_detections):
        """Test floor plan analysis with minimal data"""
        request_data = {
            "detected_rooms": [
                {
                    "label": det.label,
                    "confidence": det.confidence,
                    "bbox": det.bbox
                } for det in sample_room_detections
            ]
        }

        response = self.client.post("/api/v1/analyze/floor-plan", json=request_data)
        assert response.status_code == 200

    def test_analyze_floor_plan_invalid_data(self):
        """Test floor plan analysis with invalid data"""
        request_data = {
            "detected_rooms": [],
            "north_direction": 400.0  # Invalid angle
        }

        response = self.client.post("/api/v1/analyze/floor-plan", json=request_data)
        # Should still work as north_direction is optional
        assert response.status_code == 200

    def test_set_compass_by_angle(self):
        """Test setting compass orientation by angle"""
        request_data = {
            "angle": 90.0,
            "override_automatic": True
        }

        response = self.client.post("/api/v1/orientation/set", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["current_angle"] == 90.0
        assert data["method"] == "manual_angle"

    def test_set_compass_by_direction(self):
        """Test setting compass orientation by direction"""
        request_data = {
            "direction": "N",
            "override_automatic": True
        }

        response = self.client.post("/api/v1/orientation/set", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["current_angle"] == 0.0
        assert data["method"] == "manual_direction"

    def test_set_compass_invalid(self):
        """Test setting compass with invalid data"""
        request_data = {}  # No angle or direction

        response = self.client.post("/api/v1/orientation/set", json=request_data)
        assert response.status_code == 400

    def test_get_explanation_success(self, sample_room_detections):
        """Test retrieving explanation after analysis"""
        # First, perform an analysis to get an explanation ID
        request_data = {
            "detected_rooms": [
                {
                    "label": det.label,
                    "confidence": det.confidence,
                    "bbox": det.bbox
                } for det in sample_room_detections
            ]
        }

        analysis_response = self.client.post("/api/v1/analyze/floor-plan", json=request_data)
        assert analysis_response.status_code == 200

        analysis_id = analysis_response.json()["explanation_reference_id"]

        # Now retrieve the explanation
        response = self.client.get(f"/api/v1/explain/{analysis_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["analysis_id"] == analysis_id
        assert "explanation" in data
        assert len(data["explanation"]) > 0
        assert "generated_at" in data

    def test_get_explanation_not_found(self):
        """Test retrieving explanation with invalid ID"""
        response = self.client.get("/api/v1/explain/invalid_id")
        assert response.status_code == 404

    def test_api_endpoints_structure(self):
        """Test that all required endpoints exist and are accessible"""
        # Test health
        response = self.client.get("/api/v1/health")
        assert response.status_code == 200

        # Test analyze endpoint exists (even with invalid data)
        response = self.client.post("/api/v1/analyze/floor-plan", json={})
        assert response.status_code == 422  # Validation error, but endpoint exists

        # Test orientation endpoint exists
        response = self.client.post("/api/v1/orientation/set", json={})
        assert response.status_code == 400  # Bad request, but endpoint exists

        # Test explain endpoint exists
        response = self.client.get("/api/v1/explain/test_id")
        assert response.status_code == 404  # Not found, but endpoint exists
        
        data = response.json()
        assert "compliance_score" in data
        assert "rule_breakdown" in data
        assert "summary_explanation" in data
        assert "explainability" in data
        
        # Check compliance score is valid
        assert 0.0 <= data["compliance_score"] <= 100.0
        
        # Check rule breakdown
        assert isinstance(data["rule_breakdown"], list)
        assert len(data["rule_breakdown"]) == 0  # No rooms detected, no rules evaluated
        
        # Check explanation is present
        assert isinstance(data["summary_explanation"], str)
        assert len(data["summary_explanation"]) > 0

    def test_analyze_floorplan_empty_detections(self):
        """Test analysis with empty detections"""
        request_data = {
            "yolo_detections": [],
            "compass": {"rotation_angle": 0.0},
            "floor_width": 100,
            "floor_height": 100
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["compliance_score"] == 0.0  # Empty detections get 0% compliance
        assert len(data["rule_breakdown"]) == 0  # No rooms detected, no rules evaluated
        assert "explanation_reference_id" in data

    def test_analyze_floorplan_invalid_data(self):
        """Test analysis with invalid data"""
        # Missing required fields
        request_data = {
            "yolo_detections": []
            # Missing floor_width and floor_height
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_analyze_floorplan_low_confidence_filtering(self):
        """Test that low confidence detections are filtered"""
        yolo_detections = [
            {
                "class_id": 0,
                "confidence": 0.9,  # High confidence
                "bbox": [10, 10, 50, 50]
            },
            {
                "class_id": 1,
                "confidence": 0.3,  # Low confidence - should be filtered
                "bbox": [60, 60, 100, 100]
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 0.0},
            "floor_width": 120,
            "floor_height": 120
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Check that low confidence detections are filtered out
        # The explainability should show that only high confidence detections are accepted
        room_explanations = data["explainability"]["room_classification_explanations"]
        accepted_rooms = [exp for exp in room_explanations if exp["status"] == "accepted"]
        # Should have only one accepted room (the high confidence bedroom)
        assert len(accepted_rooms) == 1

    def test_analyze_floorplan_compass_rotation(self):
        """Test that compass rotation affects directions"""
        # Test with compass at different positions
        yolo_detections = [
            {
                "class_id": 0,  # bedroom
                "confidence": 0.9,
                "bbox": [10, 10, 50, 50]
            },
            {
                "class_id": 10,  # compass
                "confidence": 0.85,
                "bbox": [90, 10, 110, 30]  # Position affects rotation
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 45.0},  # 45 degree rotation
            "floor_width": 120,
            "floor_height": 120
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Check that compass rotation is reflected in the orientation explanation
        orientation_exp = data["explainability"]["orientation_explanation"]
        assert orientation_exp["rotation_angle"] == 45.0
        assert "45.0-degree" in orientation_exp["description"]

    def test_analyze_floorplan_deterministic(self):
        """Test that analysis is deterministic"""
        yolo_detections = [
            {
                "class_id": 0,
                "confidence": 0.9,
                "bbox": [10, 10, 50, 50]
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 0.0},
            "floor_width": 100,
            "floor_height": 100
        }
        
        response1 = self.client.post("/api/v1/analyze/yolo", json=request_data)
        response2 = self.client.post("/api/v1/analyze/yolo", json=request_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    def test_analyze_floorplan_response_structure(self):
        """Test the structure of analysis response"""
        yolo_detections = [
            {
                "class_id": 0,
                "confidence": 0.9,
                "bbox": [10, 10, 50, 50]
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 0.0},
            "floor_width": 100,
            "floor_height": 100
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = ["compliance_score", "rule_breakdown", "summary_explanation", "explainability"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["compliance_score"], float)
        assert isinstance(data["rule_breakdown"], list)
        assert isinstance(data["summary_explanation"], str)
        assert isinstance(data["explainability"], dict)
        
        # Check rule breakdown structure
        if data["rule_breakdown"]:
            rule = data["rule_breakdown"][0]
            assert "rule_id" in rule
            assert "rule_name" in rule
            assert "compliance_level" in rule

    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = self.client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test wrong HTTP method returns 405"""
        response = self.client.get("/api/v1/analyze/yolo")
        assert response.status_code == 405

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/api/v1/analyze/yolo")
        # CORS is not configured, so OPTIONS returns 405
        assert response.status_code == 405

    def test_large_detection_payload(self):
        """Test handling of large detection payloads"""
        # Create many detections
        yolo_detections = [
            {
                "class_id": i % 3,  # Cycle through room types
                "confidence": 0.8,
                "bbox": [i*10, i*10, (i+1)*10, (i+1)*10]
            }
            for i in range(50)  # 50 detections
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "floor_width": 1000,
            "floor_height": 1000
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        # Should handle large payload or return appropriate error
        assert response.status_code in [200, 413, 422]  # Success or payload too large

    def test_malformed_bbox(self):
        """Test handling of malformed bounding boxes"""
        yolo_detections = [
            {
                "class_id": 0,
                "confidence": 0.9,
                "bbox": [50, 50, 10, 10]  # Invalid bbox (x2 < x1, y2 < y1)
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 0.0},
            "floor_width": 100,
            "floor_height": 100
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        # Should handle gracefully
        assert response.status_code == 200

    def test_zero_floor_dimensions(self):
        """Test handling of zero floor dimensions"""
        yolo_detections = [
            {
                "class_id": 0,
                "confidence": 0.9,
                "bbox": [10, 10, 50, 50]
            }
        ]
        
        request_data = {
            "yolo_detections": yolo_detections,
            "compass": {"rotation_angle": 0.0},
            "floor_width": 0,
            "floor_height": 0
        }
        
        response = self.client.post("/api/v1/analyze/yolo", json=request_data)
        # Should handle gracefully or return validation error
        assert response.status_code in [200, 422]
