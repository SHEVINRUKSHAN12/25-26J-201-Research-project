from pydantic_settings import BaseSettings
from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, List, Any
import json
import os


class YOLOConfig(BaseModel):
    confidence_threshold: float = 0.5
    max_detections: int = 100
    class_mapping: Dict[str, int] = {
        "bedroom": 0,
        "dining": 1,
        "entrance": 2,
        "kitchen": 3,
        "living": 4,
        "master_bedroom": 5,  # Map to bedroom for Vastu rules
        "parking": 6,
        "pooja": 7,  # Map to living or study
        "staircase": 8,
        "store_room": 9,
        "study_room": 10,  # Map to study
        "toilet": 11,
        "utility": 12
    }
    compass_class_id: Optional[int] = None


def load_rules() -> List[Dict[str, Any]]:
    """Load Vastu compliance rules from the configuration file."""
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'core', 'rules.json')
    with open(rules_path, 'r') as f:
        return json.load(f)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Vastu Vidya Module"
    PROJECT_VERSION: str = "0.1.0"
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()
