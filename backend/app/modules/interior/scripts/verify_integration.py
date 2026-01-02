import sys
import os
from shapely.geometry import Polygon

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from backend.app.modules.interior.optimizer import GeneticOptimizer

def verify_integration():
    print("Verifying ML Model Integration...")
    
    # Dummy Data
    room_poly = Polygon([(0,0), (5,0), (5,5), (0,5)])
    furniture_items = [{"furniture_id": "test", "width": 1, "depth": 1, "rotatable": True}]
    
    # Initialize Optimizer
    try:
        optimizer = GeneticOptimizer(room_poly, furniture_items)
        
        if optimizer.ml_model is not None:
            print("✅ SUCCESS: ML Model loaded in GeneticOptimizer.")
            print(f"   Model: {optimizer.ml_model}")
        else:
            print("❌ FAILURE: ML Model is None.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    verify_integration()
