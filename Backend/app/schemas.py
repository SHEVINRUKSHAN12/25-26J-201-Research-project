from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Direction(Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


class RoomDetection(BaseModel):
    label: str = Field(..., description="Room type (e.g., bedroom, kitchen)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2]")


class Compass(BaseModel):
    rotation_angle: float = Field(..., description="Rotation angle in degrees to align true North (clockwise from image up)")


class FloorPlanInput(BaseModel):
    detections: List[RoomDetection] = Field(..., description="List of detected rooms")
    compass: Compass = Field(..., description="Compass orientation")


class RoomDirection(BaseModel):
    room: str
    direction: Direction


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    expected_direction: str
    detected_direction: str
    compliance_level: float = Field(..., ge=0.0, le=1.0)
    score_before_penalty: float
    penalty_applied: float
    final_score: float
    reasoning: str


class RawYoloDetection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x, y, w, h]")


class OrientationExplanation(BaseModel):
    method: str  # "manual_compass" or "auto_detected"
    rotation_angle: float
    description: str


class RoomClassificationExplanation(BaseModel):
    room_type: str
    confidence: float
    bbox: List[float]
    status: str  # "accepted" or "rejected"
    reasoning: str


class ComplianceRuleExplanation(BaseModel):
    rule_name: str
    expected_condition: str
    detected_condition: str
    compliance_level: float
    penalty_applied: float
    score_impact: str
    reasoning: str


class ExplainabilityResult(BaseModel):
    orientation_explanation: OrientationExplanation
    room_classification_explanations: List[RoomClassificationExplanation]
    compliance_rule_explanations: List[ComplianceRuleExplanation]
    overall_summary: str


class EnhancedComplianceResult(BaseModel):
    total_compliance_percentage: float = Field(..., ge=0.0, le=100.0)
    rule_wise_breakdown: List[RuleResult]
    summary_explanation: str
    explainability: ExplainabilityResult


class ComplianceResult(BaseModel):
    total_compliance_percentage: float = Field(..., ge=0.0, le=100.0)
    rule_wise_breakdown: List[RuleResult]
    summary_explanation: str


class RoomComplianceResult(BaseModel):
    room: str
    direction: Direction
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    is_compliant: bool
    rule_applied: str


class ComplianceRule(BaseModel):
    room: str
    preferred_directions: List[Direction]
    weight: float = Field(..., gt=0.0)
    penalty: float = Field(..., ge=0.0)


class YOLODetection(BaseModel):
    class_id: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x, y, w, h]")


class CompassDetection(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2]")


class YOLOTranslationResult(BaseModel):
    room_detections: List[RoomDetection]
    compass_detection: Optional[CompassDetection] = None


class RawFloorPlanInput(BaseModel):
    yolo_detections: List[YOLODetection]
    compass: Compass
    confidence_threshold: float = Field(0.4, ge=0.0, le=1.0)
    floor_width: int = Field(..., gt=0)
    floor_height: int = Field(..., gt=0)


# New API Models for /api/v1 endpoints

class FloorPlanAnalysisRequest(BaseModel):
    """Request model for floor plan analysis"""
    detected_rooms: List[RoomDetection] = Field(..., description="Structured room detections from YOLO")
    north_direction: Optional[float] = Field(None, description="Manual north direction in degrees (0-360)")
    compass_override: Optional[bool] = Field(False, description="Whether to override automatic compass detection")


class FloorPlanAnalysisResponse(BaseModel):
    """Response model for floor plan analysis"""
    compliance_score: float = Field(..., ge=0.0, le=100.0, description="Overall compliance percentage")
    rule_breakdown: List[RuleResult] = Field(..., description="Detailed rule-by-rule compliance results")
    explanation_reference_id: str = Field(..., description="ID to retrieve full explanation")


class CompassSetRequest(BaseModel):
    """Request model for manual compass setting"""
    angle: Optional[float] = Field(None, ge=0.0, le=360.0, description="Compass angle in degrees")
    direction: Optional[Direction] = Field(None, description="Cardinal direction")
    override_automatic: bool = Field(True, description="Whether to override automatic detection")


class CompassSetResponse(BaseModel):
    """Response model for compass setting"""
    success: bool = Field(..., description="Whether the compass was set successfully")
    current_angle: float = Field(..., ge=0.0, le=360.0, description="Current compass angle")
    method: str = Field(..., description="Method used: 'manual_angle', 'manual_direction', or 'automatic'")


class ExplanationResponse(BaseModel):
    """Response model for explanation retrieval"""
    analysis_id: str = Field(..., description="Analysis ID")
    explanation: str = Field(..., description="Full human-readable explanation")
    generated_at: str = Field(..., description="Timestamp when explanation was generated")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status: 'healthy' or 'unhealthy'")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
# Reviewed
