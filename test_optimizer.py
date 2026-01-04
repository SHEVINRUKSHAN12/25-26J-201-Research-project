"""
Test Script for Genetic Algorithm Optimizer
"""

import sys
import os
from shapely.geometry import Polygon

# Add backend to path so we can import modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.modules.interior.optimizer import GeneticOptimizer

def run_test():
    print("Running Genetic Algorithm Test...")
    
    # 1. Define a simple 4x4m room
    room_poly = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)])
    print(f"Room: 4x4m Square")
    
    # 2. Define some furniture items
    furniture_items = [
        {"id": "bed", "width": 2.0, "depth": 1.5, "rotatable": True},
        {"id": "wardrobe", "width": 1.5, "depth": 0.6, "rotatable": False},
        {"id": "desk", "width": 1.2, "depth": 0.6, "rotatable": True},
    ]
    print(f"Furniture: {[f['id'] for f in furniture_items]}")
    
    # 3. Initialize Optimizer
    optimizer = GeneticOptimizer(room_poly, furniture_items, population_size=20, generations=10)
    
    # 4. Run Optimization
    print("\nOptimizing...")
    best_layout, best_fitness = optimizer.optimize()
    
    # 5. Print Results
    print(f"\nOptimization Complete!")
    print(f"Best Fitness: {best_fitness}")
    print("\nBest Layout:")
    for i, (x, y, rot) in enumerate(best_layout):
        item = furniture_items[i]
        print(f"  {item['id']}: Pos({x:.2f}, {y:.2f}), Rot({rot}°)")
        
    if best_fitness > -100:
        print("\n✅ SUCCESS: Found a valid layout (no heavy penalties)!")
    else:
        print("\n❌ FAILURE: Could not satisfy hard constraints.")

if __name__ == "__main__":
    run_test()
