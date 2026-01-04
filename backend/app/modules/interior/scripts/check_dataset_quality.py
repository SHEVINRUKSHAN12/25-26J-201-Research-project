import json
import sys
import os
from pathlib import Path
import random

# Add backend directory to sys.path to allow imports
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent.parent.parent
sys.path.append(str(backend_dir))

from app.modules.interior.fitness import FitnessEvaluator
from app.modules.interior.constraints import ConstraintChecker
from shapely.geometry import Polygon

def check_dataset_quality(sample_size=50):
    print(f"Checking dataset quality (Sample size: {sample_size} per room type)...")
    
    dataset_dir = Path("datasets")
    room_types = ["bedroom", "living_room", "kitchen", "bathroom", "dining_room", "apartment"]
    
    total_samples = 0
    valid_layouts = 0
    consistent_scores = 0
    total_error = 0.0
    
    for room_type in room_types:
        room_path = dataset_dir / room_type
        if not room_path.exists():
            continue
            
        files = list(room_path.glob("*.json"))
        if not files:
            continue
            
        # Take a random sample
        sample_files = random.sample(files, min(len(files), sample_size))
        
        print(f"\nAnalyzing {room_type} ({len(sample_files)} samples):")
        
        room_valid = 0
        room_consistent = 0
        
        for file_path in sample_files:
            total_samples += 1
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct Room Polygon
                room_dims = data['room_dimensions']
                room_poly = Polygon([
                    (0, 0),
                    (room_dims['width'], 0),
                    (room_dims['width'], room_dims['length']),
                    (0, room_dims['length'])
                ])
                
                # Reconstruct Furniture Items & Layout
                furniture_items = []
                layout = []
                
                for item in data['furniture_layout']:
                    # Reconstruct item dict expected by ConstraintChecker
                    # We need width/depth. The dataset stores them.
                    furniture_item = {
                        "id": item['id'],
                        "width": item['width'],
                        "depth": item['depth'],
                        "height": item.get('height', 1.0),
                        "category": item.get('category', 'unknown'),
                        "type": item.get('type', 'unknown')
                    }
                    furniture_items.append(furniture_item)
                    layout.append((item['x'], item['y'], item['rotation']))
                
                # Initialize Evaluator
                constraints = ConstraintChecker(room_poly, furniture_items)
                evaluator = FitnessEvaluator(room_poly, furniture_items, constraints)
                
                # Recalculate Fitness
                calculated_raw_fitness = evaluator.calculate_fitness(layout)
                
                # Compare with stored score
                # Note: The dataset might store raw or normalized score. 
                # Usually datasets for ML store the raw score or a specific target.
                # Let's assume 'fitness_score' in JSON is what we want to check.
                stored_score = data['fitness_score']
                
                # Check Validity (Hard Constraints)
                # If calculated score is negative, it means constraints were violated
                is_valid = calculated_raw_fitness >= 0
                
                if is_valid:
                    room_valid += 1
                    valid_layouts += 1
                
                # Check Consistency
                # Allow small floating point error
                error = abs(calculated_raw_fitness - stored_score)
                total_error += error
                
                if error < 0.001:
                    room_consistent += 1
                    consistent_scores += 1
                else:
                    # Only print first few errors
                    if total_samples <= 5:
                        print(f"  [MISMATCH] {file_path.name}: Stored={stored_score:.4f}, Calc={calculated_raw_fitness:.4f}, Diff={error:.4f}")

            except Exception as e:
                print(f"  [ERROR] Failed to process {file_path.name}: {e}")

        print(f"  Valid Layouts: {room_valid}/{len(sample_files)} ({room_valid/len(sample_files)*100:.1f}%)")
        print(f"  Consistent Scores: {room_consistent}/{len(sample_files)} ({room_consistent/len(sample_files)*100:.1f}%)")

    print("\n" + "="*30)
    print("OVERALL RESULTS")
    print("="*30)
    print(f"Total Samples Checked: {total_samples}")
    print(f"Valid Layouts (No Overlap): {valid_layouts} ({valid_layouts/total_samples*100:.1f}%)")
    print(f"Label Accuracy (Score Match): {consistent_scores} ({consistent_scores/total_samples*100:.1f}%)")
    print(f"Mean Absolute Error: {total_error/total_samples:.6f}")
    
    if valid_layouts == total_samples and consistent_scores == total_samples:
        print("\n[SUCCESS] Dataset is 100% Accurate and Valid.")
    else:
        print("\n[WARNING] Dataset has potential issues.")

if __name__ == "__main__":
    check_dataset_quality()
