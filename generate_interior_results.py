"""
Generate REAL Interior Optimization Results for Research Paper
Runs actual tests and outputs table data for LaTeX
"""

import sys
import os
import time
from shapely.geometry import Polygon

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.modules.interior.optimizer import GeneticOptimizer

def test_scenario(name, room_coords, furniture_items, pop_size=50, generations=100):
    """Run optimization and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    room_poly = Polygon(room_coords)
    room_area = room_poly.area
    
    print(f"Room Area: {room_area:.1f} m²")
    print(f"Furniture Items: {len(furniture_items)}")
    for item in furniture_items:
        print(f"  - {item['id']}: {item['width']}m × {item['depth']}m")
    
    # Initialize optimizer
    optimizer = GeneticOptimizer(
        room_poly, 
        furniture_items, 
        population_size=pop_size, 
        generations=generations
    )
    
    # Run optimization and measure time
    start_time = time.time()
    best_layout, best_fitness = optimizer.optimize()
    execution_time = time.time() - start_time
    
    # Determine status
    if best_fitness >= 0:
        status = "Valid"
    elif best_fitness > -100:
        status = "Partial"
    else:
        status = "Failed"
    
    print(f"\n✅ RESULTS:")
    print(f"  Best Fitness: {best_fitness:.1f}")
    print(f"  Execution Time: {execution_time:.1f}s")
    print(f"  Status: {status}")
    
    return {
        "name": name,
        "area": room_area,
        "items": len(furniture_items),
        "fitness": best_fitness,
        "time": execution_time,
        "status": status
    }

def main():
    print("="*60)
    print("INTERIOR SPACE OPTIMIZATION - REAL EXPERIMENTAL RESULTS")
    print("="*60)
    
    results = []
    
    # Test 1: Bedroom (14 m² ≈ 3.7m × 3.8m)
    bedroom_room = [(0, 0), (3.7, 0), (3.7, 3.8), (0, 3.8)]
    bedroom_furniture = [
        {"id": "bed", "width": 2.0, "depth": 1.5, "rotatable": True},
        {"id": "wardrobe", "width": 1.5, "depth": 0.6, "rotatable": False},
        {"id": "desk", "width": 1.2, "depth": 0.6, "rotatable": True},
        {"id": "chair", "width": 0.5, "depth": 0.5, "rotatable": True}
    ]
    results.append(test_scenario("Bedroom", bedroom_room, bedroom_furniture))
    
    # Test 2: Living Room (18 m² ≈ 4.5m × 4m)
    living_room = [(0, 0), (4.5, 0), (4.5, 4.0), (0, 4.0)]
    living_furniture = [
        {"id": "sofa", "width": 2.0, "depth": 0.9, "rotatable": True},
        {"id": "coffee_table", "width": 1.2, "depth": 0.6, "rotatable": True},
        {"id": "tv_stand", "width": 1.5, "depth": 0.4, "rotatable": False},
        {"id": "bookshelf", "width": 0.8, "depth": 0.3, "rotatable": False},
        {"id": "armchair", "width": 0.9, "depth": 0.9, "rotatable": True}
    ]
    results.append(test_scenario("Living Room", living_room, living_furniture))
    
    # Test 3: Kitchen (10 m² ≈ 3.2m × 3.1m)
    kitchen_room = [(0, 0), (3.2, 0), (3.2, 3.1), (0, 3.1)]
    kitchen_furniture = [
        {"id": "dining_table", "width": 1.2, "depth": 0.8, "rotatable": True},
        {"id": "chair_1", "width": 0.5, "depth": 0.5, "rotatable": True},
        {"id": "cabinet", "width": 1.0, "depth": 0.5, "rotatable": False}
    ]
    results.append(test_scenario("Kitchen", kitchen_room, kitchen_furniture))
    
    # Test 4: Compact Bedroom (9 m² ≈ 3m × 3m) - Tight space
    compact_room = [(0, 0), (3.0, 0), (3.0, 3.0), (0, 3.0)]
    compact_furniture = [
        {"id": "bed", "width": 1.9, "depth": 1.4, "rotatable": True},
        {"id": "wardrobe", "width": 1.2, "depth": 0.5, "rotatable": False},
        {"id": "desk", "width": 1.0, "depth": 0.5, "rotatable": True},
        {"id": "chair", "width": 0.5, "depth": 0.5, "rotatable": True}
    ]
    results.append(test_scenario("Compact Bedroom", compact_room, compact_furniture))
    
    # Generate LaTeX table
    print("\n" + "="*60)
    print("LATEX TABLE OUTPUT")
    print("="*60)
    print("\n\\begin{table}[htbp]")
    print("\\caption{Interior Space Optimization Results}")
    print("\\label{tab:interior_optimization}")
    print("\\centering")
    print("\\small")
    print("\\begin{tabular}{lccccc}")
    print("\\toprule")
    print("\\textbf{Room} & \\textbf{Area (m$^2$)} & \\textbf{Items} & \\textbf{Fitness} & \\textbf{Time (s)} & \\textbf{Status} \\\\")
    print("\\midrule")
    
    for r in results:
        print(f"{r['name']} & {r['area']:.0f} & {r['items']} & {r['fitness']:.1f} & {r['time']:.1f} & {r['status']} \\\\")
    
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")
    
    # Save to file
    with open("interior_results.txt", "w") as f:
        f.write("INTERIOR OPTIMIZATION EXPERIMENTAL RESULTS\n")
        f.write("="*60 + "\n\n")
        for r in results:
            f.write(f"{r['name']}:\n")
            f.write(f"  Area: {r['area']:.1f} m²\n")
            f.write(f"  Items: {r['items']}\n")
            f.write(f"  Fitness: {r['fitness']:.1f}\n")
            f.write(f"  Time: {r['time']:.1f}s\n")
            f.write(f"  Status: {r['status']}\n\n")
    
    print("\n✅ Results saved to: interior_results.txt")

if __name__ == "__main__":
    main()
