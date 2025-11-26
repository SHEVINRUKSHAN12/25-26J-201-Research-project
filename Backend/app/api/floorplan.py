from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import (
    FloorPlanAnalysisRequest, FloorPlanAnalysisResponse,
    CompassSetRequest, CompassSetResponse,
    ExplanationResponse, HealthResponse,
    Compass, RoomDirection, ComplianceResult, ComplianceRule, Direction,
    RawFloorPlanInput
)
from app.services.direction import calculate_room_directions
from app.services.compliance import ComplianceEngine
from app.services.explainability import ExplainabilityService
from app.services.orientation import OrientationService
from app.services.yolo_integration import YOLOIntegrationService
from app.core.config import load_rules, YOLOConfig

# Create sub-routers for logical grouping
analyze_router = APIRouter(prefix="/analyze", tags=["Analysis"])
orientation_router = APIRouter(prefix="/orientation", tags=["Orientation"])
explain_router = APIRouter(prefix="/explain", tags=["Explainability"])
health_router = APIRouter(prefix="/health", tags=["Health"])

# In-memory storage for explanations (in production, use database)
explanation_store: Dict[str, str] = {}


# Dependency injection functions
def get_compliance_engine() -> ComplianceEngine:
    rules_data = load_rules()
    # Transform rules to match ComplianceRule model
    rules = []
    for rule_data in rules_data:
        if "applicable_room_types" in rule_data and rule_data["applicable_room_types"]:
            # Create a rule for each applicable room type
            for room_type in rule_data["applicable_room_types"]:
                # Convert direction strings to Direction enums
                preferred_directions = []
                for dir_str in rule_data.get("preferred_directions", []):
                    try:
                        preferred_directions.append(Direction(dir_str))
                    except ValueError:
                        # Skip invalid directions
                        continue

                if preferred_directions:  # Only add if we have valid directions
                    rule = ComplianceRule(
                        room=room_type,
                        preferred_directions=preferred_directions,
                        weight=rule_data.get("weight", 1.0),
                        penalty=rule_data.get("penalty_factor", 0.0)
                    )
                    rules.append(rule)
    return ComplianceEngine(rules)

def get_explainability_service() -> ExplainabilityService:
    return ExplainabilityService()

def get_orientation_service() -> OrientationService:
    return OrientationService()

def get_yolo_integration_service() -> YOLOIntegrationService:
    config = YOLOConfig()
    return YOLOIntegrationService(config)


@analyze_router.post("/floor-plan", response_model=FloorPlanAnalysisResponse)
async def analyze_floor_plan(
    request: FloorPlanAnalysisRequest,
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine),
    explainability_service: ExplainabilityService = Depends(get_explainability_service)
) -> FloorPlanAnalysisResponse:
    """
    Analyze floor plan for Vastu compliance.

    Receives structured room detections and optional compass overrides.
    Returns compliance score, rule breakdown, and explanation reference ID.
    """
    try:
        # Create compass object
        compass = Compass(rotation_angle=request.north_direction or 0.0)

        # Calculate room directions
        room_directions = calculate_room_directions(request.detected_rooms, compass)

        # Evaluate compliance
        compliance_result = compliance_engine.evaluate_compliance(room_directions)

        # Generate explanation and store it
        explanation = explainability_service.generate_explanation(compliance_result)
        analysis_id = f"analysis_{datetime.utcnow().timestamp()}"
        explanation_store[analysis_id] = explanation

        return FloorPlanAnalysisResponse(
            compliance_score=compliance_result.total_compliance_percentage,
            rule_breakdown=compliance_result.rule_wise_breakdown,
            explanation_reference_id=analysis_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}. Please verify input data format."
        )


@analyze_router.post("/yolo", response_model=FloorPlanAnalysisResponse)
async def analyze_floor_plan_yolo(
    request: RawFloorPlanInput,
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine),
    explainability_service: ExplainabilityService = Depends(get_explainability_service),
    yolo_service: YOLOIntegrationService = Depends(get_yolo_integration_service)
) -> FloorPlanAnalysisResponse:
    """
    Analyze floor plan from raw YOLO detections for Vastu compliance.

    Receives raw YOLO detections and processes them into structured room data.
    Returns compliance score, rule breakdown, and explanation reference ID.
    """
    try:
        # Process YOLO detections into structured room detections
        translation_result = yolo_service.translate_detections(request.yolo_detections)

        # Create compass object (use detected compass if available, otherwise use provided)
        compass_rotation = request.compass.rotation_angle
        if translation_result.compass_detection:
            # Calculate compass rotation relative to floor center
            floor_center = (request.floor_width / 2, request.floor_height / 2)
            compass_rotation = yolo_service._calculate_compass_rotation(
                translation_result.compass_detection, floor_center
            )

        compass = Compass(rotation_angle=compass_rotation)

        # Calculate room directions
        room_directions = calculate_room_directions(translation_result.room_detections, compass)

        # Evaluate compliance
        compliance_result = compliance_engine.evaluate_compliance(room_directions)

        # Generate explanation and store it
        explanation = explainability_service.generate_explanation(compliance_result)
        analysis_id = f"analysis_{datetime.utcnow().timestamp()}"
        explanation_store[analysis_id] = explanation

        return FloorPlanAnalysisResponse(
            compliance_score=compliance_result.total_compliance_percentage,
            rule_breakdown=compliance_result.rule_wise_breakdown,
            explanation_reference_id=analysis_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"YOLO analysis failed: {str(e)}. Please verify YOLO detection format."
        )


@orientation_router.post("/set", response_model=CompassSetResponse)
async def set_compass_orientation(
    request: CompassSetRequest,
    orientation_service: OrientationService = Depends(get_orientation_service)
) -> CompassSetResponse:
    """
    Manually set compass orientation for floor plan analysis.

    Accepts either an angle in degrees or a cardinal direction.
    Overrides automatic north detection if specified.
    """
    try:
        if request.angle is not None:
            # Set by angle
            success = orientation_service.set_manual_angle(request.angle)
            return CompassSetResponse(
                success=success,
                current_angle=request.angle,
                method="manual_angle"
            )
        elif request.direction is not None:
            # Set by direction
            angle = orientation_service.direction_to_angle(request.direction)
            success = orientation_service.set_manual_angle(angle)
            return CompassSetResponse(
                success=success,
                current_angle=angle,
                method="manual_direction"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'angle' or 'direction' must be provided."
            )

    except HTTPException:
        raise  # Re-raise HTTPException
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compass setting failed: {str(e)}. Please verify input parameters."
        )


@explain_router.get("/{analysis_id}", response_model=ExplanationResponse)
async def get_explanation(
    analysis_id: str,
    explainability_service: ExplainabilityService = Depends(get_explainability_service)
) -> ExplanationResponse:
    """
    Retrieve full human-readable explanation for a completed analysis.

    Returns detailed compliance reasoning and recommendations.
    """
    try:
        if analysis_id not in explanation_store:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis ID '{analysis_id}' not found. Please ensure the analysis was completed successfully."
            )

        explanation = explanation_store[analysis_id]

        return ExplanationResponse(
            analysis_id=analysis_id,
            explanation=explanation,
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation retrieval failed: {str(e)}. Please try again."
        )


@health_router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Simple health check endpoint.

    Returns service status and version information.
    """
    return HealthResponse(
        status="healthy",
        version="v1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


# Main router that combines all sub-routers
router = APIRouter(prefix="/api/v1")
router.include_router(analyze_router)
router.include_router(orientation_router)
router.include_router(explain_router)
router.include_router(health_router)
# Reviewed
