from __future__ import annotations

import math
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter()
_JOBS: dict[str, dict[str, Any]] = {}


class ArcplanRequest(BaseModel):
    shape: str = Field(default="rectangular")
    width: float | None = None
    height: float | None = None
    main_width: float | None = None
    main_depth: float | None = None
    extension_width: float | None = None
    extension_depth: float | None = None
    extension_side: str = "right"
    bedrooms: int = 3
    toilets: int = 2
    kitchen: bool = True
    living: bool = True
    dining: bool = True
    carport: bool = False
    front: str = "S"


ROOM_MIN_AREA = {
    "living": 18,
    "dining": 12,
    "kitchen": 10,
    "master_bedroom": 14,
    "bedroom": 10,
    "toilet": 4,
    "carport": 16,
}


def _num(value: float | None, fallback: float) -> float:
    try:
        if value is None or not math.isfinite(float(value)):
            return fallback
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _build_rooms(data: ArcplanRequest, buildable_area: float) -> list[dict[str, Any]]:
    rooms: list[dict[str, Any]] = []
    if data.living:
        rooms.append({"type": "living", "name": "Living", "area": ROOM_MIN_AREA["living"]})
    if data.dining:
        rooms.append({"type": "dining", "name": "Dining", "area": ROOM_MIN_AREA["dining"]})
    if data.kitchen:
        rooms.append({"type": "kitchen", "name": "Kitchen", "area": ROOM_MIN_AREA["kitchen"]})

    bedroom_count = max(1, min(6, data.bedrooms))
    rooms.append({"type": "master_bedroom", "name": "Master Bedroom", "area": ROOM_MIN_AREA["master_bedroom"]})
    for index in range(max(0, bedroom_count - 1)):
        rooms.append({"type": "bedroom", "name": f"Bedroom {index + 2}", "area": ROOM_MIN_AREA["bedroom"]})

    for index in range(max(1, min(4, data.toilets))):
        rooms.append({"type": "toilet", "name": f"Toilet {index + 1}", "area": ROOM_MIN_AREA["toilet"]})
    if data.carport:
        rooms.append({"type": "carport", "name": "Carport", "area": ROOM_MIN_AREA["carport"]})

    requested_area = sum(room["area"] for room in rooms)
    scale = max(0.6, min(1.35, buildable_area / max(requested_area, 1)))
    for room in rooms:
        room_area = room["area"] * scale
        ratio = 1.25 if room["type"] not in {"toilet", "carport"} else 1.0
        room["w"] = round(math.sqrt(room_area * ratio), 2)
        room["h"] = round(room_area / room["w"], 2)
        room["area"] = round(room_area, 2)
    return rooms


def _zones_for_rect(width: float, height: float) -> tuple[dict[str, float], list[dict[str, Any]]]:
    front, rear, side = 3.0, 1.5, 1.5
    buildable = {
        "x": side,
        "y": front,
        "w": max(1, width - side * 2),
        "h": max(1, height - front - rear),
    }
    zones = [
        {"type": "setback", "label": "Front Setback", "x": 0, "y": 0, "w": width, "h": front, "color": "#dbeafe"},
        {"type": "setback", "label": "Rear Setback", "x": 0, "y": height - rear, "w": width, "h": rear, "color": "#dcfce7"},
        {"type": "setback", "label": "Side Setback", "x": 0, "y": front, "w": side, "h": height - front - rear, "color": "#fef3c7"},
        {"type": "setback", "label": "Side Setback", "x": width - side, "y": front, "w": side, "h": height - front - rear, "color": "#fef3c7"},
    ]
    return buildable, zones


def _optimize(data: ArcplanRequest) -> dict[str, Any]:
    shape = data.shape.lower().replace("-", "").replace("_", "")
    if shape == "lshape":
        main_width = _num(data.main_width, 12)
        main_depth = _num(data.main_depth, 15)
        extension_width = _num(data.extension_width, 8)
        extension_depth = _num(data.extension_depth, 10)
        main_zone = {"x": 1.5, "y": 3.0, "w": max(1, main_width - 3), "h": max(1, main_depth - 4.5)}
        if data.extension_side == "left":
            extension_zone = {"x": 1.5, "y": 3.0, "w": max(1, extension_width - 1.5), "h": max(1, extension_depth - 3)}
        else:
            extension_zone = {"x": main_width, "y": 3.0, "w": max(1, extension_width - 1.5), "h": max(1, extension_depth - 3)}
        buildable_area = main_zone["w"] * main_zone["h"]
        land = {
            "shape": "lshape",
            "main_width": main_width,
            "main_depth": main_depth,
            "extension_width": extension_width,
            "extension_depth": extension_depth,
            "extension_side": data.extension_side,
            "front_orientation": data.front,
        }
        return {
            "land": land,
            "front_orientation": data.front,
            "buildable_zone": main_zone,
            "lshape_data": {"main_zone": main_zone, "extension_zone": extension_zone, "extension_side": data.extension_side},
            "rooms": _build_rooms(data, buildable_area),
            "zones": [],
            "score": round(min(96, 68 + buildable_area / 8), 1),
            "feasible": buildable_area >= 45,
        }

    width = _num(data.width, 20)
    height = _num(data.height, 25)
    buildable, zones = _zones_for_rect(width, height)
    buildable_area = buildable["w"] * buildable["h"]
    return {
        "land": {"shape": "rectangular", "width": width, "height": height, "front_orientation": data.front},
        "front_orientation": data.front,
        "buildable_zone": buildable,
        "rooms": _build_rooms(data, buildable_area),
        "zones": zones,
        "score": round(min(98, 70 + buildable_area / 18), 1),
        "feasible": buildable_area >= 45,
    }


@router.post("/optimize")
def optimize(data: ArcplanRequest):
    job_id = uuid.uuid4().hex[:8]
    result = _optimize(data)
    _JOBS[job_id] = {
        "status": "done",
        "progress": 100,
        "gen": 60,
        "current_score": result["score"],
        "result": result,
        "log": ["Optimization completed"],
    }
    return {"job_id": job_id, "status": "started"}


@router.get("/status/{job_id}")
def status(job_id: str):
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {key: job[key] for key in ("status", "progress", "gen", "current_score", "log")}


@router.get("/result/{job_id}")
def result(job_id: str):
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job["result"]
