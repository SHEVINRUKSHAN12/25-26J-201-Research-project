"""
Generate REAL Bedroom Optimization Results for Research Paper
Tests only bedroom scenarios with realistic dimensions
"""

import sys
import os
import time
from shapely.geometry import Polygon

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.modules.interior.optimizer import GeneticOptimizer

def test_bedroom(name, width, length, furniture_items):
    """Run bedroom optimization test"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Dimensions: {width}m × {length}m = {width*length:.1f}m²")
    print(f"{'='*60}")
    
    room_coords = [(0, 0), (width, 0), (width, length), (0, length)]
    room_poly = Polygon(room_coords)
    
    print(f"Furniture Items ({len(furniture_items)}):")
    for item in furniture_items:
        print(f"  - {item['id']}: {item['width']}m × {item['depth']}m")
    
    optimizer = GeneticOptimizer(room_poly, furniture_items, population_size=50, generations=30)
    
    start_time = time.time()
    best_layout, best_fitness = optimizer.optimize()
    execution_time = time.time() - start_time
    
    if best_fitness >= 0:
        status = "Valid"
    elif best_fitness > -100:
        status = "Partial"
    else:
        status = "Failed"
    
    print(f"\n✅ RESULTS:")
    print(f"  Fitness: {best_fitness:.1f}")
    print(f"  Time: {execution_time:.1f}s")
    print(f"  Status: {status}")
    
    return {
        "name": name,
        "area": width * length,
        "items": len(furniture_items),
        "fitness": best_fitness,
        "time": execution_time,
        "status": status
    }

def main():
    print("="*60)
    print("BEDROOM OPTIMIZATION - REAL EXPERIMENTAL RESULTS")
    print("="*60)
    
    results = []
    
    # Standard bedroom furniture
    standard_furniture = [
        {"id": "bed", "width": 2.0, "depth": 1.5, "rotatable": True},
        {"id": "wardrobe", "width": 1.5, "depth": 0.6, "rotatable": False},
        {"id": "desk", "width": 1.2, "depth": 0.6, "rotatable": True},
        {"id": "chair", "width": 0.5, "depth": 0.5, "rotatable": True}
    ]
    
    # Test 1: Medium Bedroom (14 m²)
    results.append(test_bedroom("Bedroom", 4.0, 3.5, standard_furniture))
    
    # Test 2: Large Bedroom (18 m²)
    results.append(test_bedroom("Large Bedroom", 4.5, 4.0, standard_furniture))
    
    # Test 3: Small Bedroom (10 m²)
    small_furniture = [
        {"id": "bed", "width": 1.9, "depth": 1.4, "rotatable": True},
        {"id": "wardrobe", "width": 1.2, "depth": 0.5, "rotatable": False},
        {"id": "desk", "width": 1.0, "depth": 0.5, "rotatable": True}
    ]
    results.append(test_bedroom("Small Bedroom", 3.2, 3.1, small_furniture))
    
    # Test 4: Compact Bedroom (9 m²) - Challenging
    compact_furniture = [
        {"id": "bed", "width": 1.9, "depth": 1.4, "rotatable": True},
        {"id": "wardrobe", "width": 1.2, "depth": 0.5, "rotatable": False},
        {"id": "desk", "width": 1.0, "depth": 0.5, "rotatable": True},
        {"id": "chair", "width": 0.5, "depth": 0.5, "rotatable": True}
    ]
    results.append(test_bedroom("Compact Bedroom", 3.0, 3.0, compact_furniture))
    
    # Generate LaTeX table
    print("\n" + "="*60)
    print("LATEX TABLE FOR PAPER")
    print("="*60 + "\n")
    print("\\begin{table}[htbp]")
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
    
    # Save results
    with open("bedroom_results.txt", "w") as f:
        f.write("BEDROOM OPTIMIZATION RESULTS\n")
        f.write("="*60 + "\n\n")
        for r in results:
            f.write(f"{r['name']}:\n")
            f.write(f"  Area: {r['area']:.1f} m²\n")
            f.write(f"  Items: {r['items']}\n")
            f.write(f"  Fitness: {r['fitness']:.1f}\n")
            f.write(f"  Time: {r['time']:.1f}s\n")
            f.write(f"  Status: {r['status']}\n\n")
        
        f.write("\nLATEX TABLE:\n")
        f.write("\\begin{table}[htbp]\n")
        f.write("\\caption{Interior Space Optimization Results}\n")
        f.write("\\label{tab:interior_optimization}\n")
        f.write("\\centering\n")
        f.write("\\small\n")
        f.write("\\begin{tabular}{lccccc}\n")
        f.write("\\toprule\n")
        f.write("\\textbf{Room} & \\textbf{Area (m$^2$)} & \\textbf{Items} & \\textbf{Fitness} & \\textbf{Time (s)} & \\textbf{Status} \\\\\n")
        f.write("\\midrule\n")
        for r in results:
            f.write(f"{r['name']} & {r['area']:.0f} & {r['items']} & {r['fitness']:.1f} & {r['time']:.1f} & {r['status']} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    
    print("\n✅ Results saved to: bedroom_results.txt")

if __name__ == "__main__":
    main()
