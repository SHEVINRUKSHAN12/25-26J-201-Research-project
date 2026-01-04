"""
Interior Optimization API Endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from shapely.geometry import Polygon
from app.modules.interior.optimizer import GeneticOptimizer

router = APIRouter()

class FurnitureItem(BaseModel):
    id: str
    width: float
    depth: float
    height: float = 0.0
    rotatable: bool = True
    category: str = "misc"

class RoomPolygon(BaseModel):
    points: List[List[float]] # [[x1,y1], [x2,y2], ...]

class OptimizationRequest(BaseModel):
    room_polygon: List[List[float]]
    furniture_items: List[FurnitureItem]
    constraints: Optional[Dict[str, Any]] = {}

class OptimizationResponse(BaseModel):
    fitness: float
    score_percentage: float
    layout: List[Dict[str, Any]] # [{"id": "bed", "x": 1.2, "y": 3.0, "rotation": 90}, ...]

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_interior(request: OptimizationRequest):
    try:
        # 1. Convert input to internal format
        room_poly = Polygon(request.room_polygon)
        
        furniture_data = []
        for item in request.furniture_items:
            furniture_data.append({
                "id": item.id,
                "width": item.width,
                "depth": item.depth,
                "height": item.height,
                "rotatable": item.rotatable,
                "category": item.category
            })
            
        # 2. Run Genetic Algorithm
        # Use more generations for better quality, especially in small rooms
        optimizer = GeneticOptimizer(
            room_poly, 
            furniture_data, 
            population_size=100, 
            generations=150
        )
        
        best_layout, best_fitness = optimizer.optimize()
        
        # Calculate percentage
        score_pct = optimizer.evaluator.calculate_normalized_score(best_fitness)
        
        # 3. Format output
        formatted_layout = []
        for i, (x, y, rot) in enumerate(best_layout):
            item_id = furniture_data[i]["id"]
            formatted_layout.append({
                "id": item_id,
                "x": round(x, 2),
                "y": round(y, 2),
                "rotation": rot
            })
            
        return {
            "fitness": best_fitness,
            "score_percentage": round(score_pct, 1),
            "layout": formatted_layout
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
