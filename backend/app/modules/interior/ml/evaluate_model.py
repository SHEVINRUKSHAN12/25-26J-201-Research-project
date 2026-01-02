"""
Model Evaluation Script
Calculates R² Score, MSE, and Accuracy metrics for the trained model.
"""
import json
import torch
import numpy as np
from pathlib import Path
import sys
import os
import random

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))
from backend.app.modules.interior.ml.model import InteriorFitnessModel

def calculate_r2(y_true, y_pred):
    """Calculate R² (Coefficient of Determination)"""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

def calculate_accuracy(y_true, y_pred, tolerance=0.1):
    """
    Calculate accuracy based on tolerance.
    A prediction is 'correct' if it's within tolerance of the true value.
    """
    correct = np.sum(np.abs(y_true - y_pred) < tolerance)
    return correct / len(y_true) * 100

def evaluate_model():
    print("="*50)
    print("MODEL EVALUATION REPORT")
    print("="*50)
    
    # Load validation data
    val_path = Path("processed_data/val.json")
    if not val_path.exists():
        print("[ERROR] Validation data not found!")
        return
        
    with open(val_path, 'r') as f:
        val_data = json.load(f)
    
    print(f"Validation Set Size: {len(val_data)} scenarios")
    
    # Load Best Model
    model_path = Path("backend/app/modules/interior/ml/models/best_model.pth")
    if not model_path.exists():
        print("[ERROR] Trained model not found!")
        return
        
    model = InteriorFitnessModel(input_size=7)
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    model.eval()
    
    print(f"Model Loaded: {model_path}")
    
    # Prepare Test Features (simplified, matching training)
    y_true = []
    y_pred = []
    
    # Imports for fitness calculation
    from backend.app.modules.interior.fitness import FitnessEvaluator
    from backend.app.modules.interior.constraints import ConstraintChecker
    from backend.app.modules.interior.geometry import create_room_polygon
    
    for scenario in val_data:
        # Extract features (same as training)
        room_area = scenario["room_area"] / 50.0
        aspect_ratio = scenario["room_aspect_ratio"] / 2.0
        num_doors = scenario["num_doors"] / 4.0
        num_windows = scenario["num_windows"] / 4.0
        num_furniture = scenario["num_furniture"] / 20.0
        
        # Reconstruct Room & Furniture for Ground Truth Calculation
        room_poly_coords = scenario["original"]["room_polygon"]
        room_poly = create_room_polygon(room_poly_coords)
        doors = scenario["original"].get("doors", [])
        windows = scenario["original"].get("windows", [])
        furniture_items = scenario["original"]["selected_furniture"]
        
        # Initialize Evaluator
        constraints = ConstraintChecker(room_poly, doors, windows)
        evaluator = FitnessEvaluator(room_poly, furniture_items, constraints)
        
        # We need to evaluate the specific layout in the scenario
        # But wait, the scenario in val.json might NOT have a specific layout position for items if it's just the room definition.
        # train.py generates RANDOM layouts.
        # If val.json is just room definitions, we need to generate a layout to test the model.
        
        # Let's generate a random layout, calculate its true score, and see if model predicts it.
        # This matches train.py logic.
        
        min_x, min_y, max_x, max_y = room_poly.bounds
        current_layout_items = []
        
        for item in furniture_items:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            rotation = random.choice([0, 90, 180, 270]) if item["rotatable"] else 0
            
            placed_item = item.copy()
            placed_item["position"] = {"x": x, "y": y}
            placed_item["rotation"] = rotation
            current_layout_items.append(placed_item)
            
        # 1. Calculate Ground Truth
        try:
            raw_score = evaluator.evaluate(room_poly, current_layout_items)
        except:
            raw_score = -100
            
        true_score = max(-1.0, min(1.0, raw_score / 100.0))
        
        # 2. Prepare Model Input
        # Calculate layout features
        avg_x = sum(i["position"]["x"] for i in current_layout_items) / len(current_layout_items)
        avg_y = sum(i["position"]["y"] for i in current_layout_items) / len(current_layout_items)
        
        width = max_x - min_x
        height = max_y - min_y
        norm_avg_x = avg_x / width if width > 0 else 0
        norm_avg_y = avg_y / height if height > 0 else 0
        
        features = torch.tensor([room_area, aspect_ratio, num_doors, num_windows, 
                                  num_furniture, norm_avg_x, norm_avg_y], dtype=torch.float32)
        
        # 3. Model Prediction
        with torch.no_grad():
            pred_score = model(features.unsqueeze(0)).item()
        
        y_true.append(true_score)
        y_pred.append(pred_score)
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Calculate Metrics
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    r2 = calculate_r2(y_true, y_pred)
    accuracy_10 = calculate_accuracy(y_true, y_pred, tolerance=0.1)
    accuracy_15 = calculate_accuracy(y_true, y_pred, tolerance=0.15)
    accuracy_20 = calculate_accuracy(y_true, y_pred, tolerance=0.2)
    
    print("\n" + "-"*30)
    print("EVALUATION METRICS")
    print("-"*30)
    print(f"MSE (Mean Squared Error):      {mse:.6f}")
    print(f"RMSE (Root Mean Squared Error): {rmse:.4f}")
    print(f"MAE (Mean Absolute Error):     {mae:.4f}")
    print(f"R² Score:                      {r2:.4f} ({r2*100:.2f}%)")
    print("-"*30)
    print("ACCURACY (within tolerance)")
    print("-"*30)
    print(f"Accuracy (±10% tolerance):     {accuracy_10:.1f}%")
    print(f"Accuracy (±15% tolerance):     {accuracy_15:.1f}%")
    print(f"Accuracy (±20% tolerance):     {accuracy_20:.1f}%")
    print("="*50)
    
    # Summary
    print("\nSUMMARY FOR PRESENTATION:")
    print(f"  Model R² Score: {r2*100:.1f}%")
    print(f"  Prediction Accuracy: {accuracy_15:.1f}% (±15% tolerance)")

if __name__ == "__main__":
    evaluate_model()
