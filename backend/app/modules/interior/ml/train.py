import json
import os
import sys
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path

# Add backend to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from backend.app.modules.interior.ml.model import InteriorFitnessModel
# We need to import FitnessEvaluator to generate ground truth labels
# Assuming fitness.py is in backend/app/modules/interior/fitness.py
from backend.app.modules.interior.fitness import FitnessEvaluator
from backend.app.modules.interior.constraints import ConstraintChecker
from backend.app.modules.interior.geometry import create_room_polygon

class InteriorDataset(Dataset):
    def __init__(self, data_path, samples_per_room=5):
        """
        data_path: Path to train.json or val.json
        samples_per_room: Number of random layouts to generate per room scenario
        """
        with open(data_path, 'r') as f:
            self.scenarios = json.load(f)
            
        self.samples_per_room = samples_per_room
        self.data = []
        self.labels = []
        
        print(f"Generating training samples from {len(self.scenarios)} scenarios...")
        self._generate_samples()
        
    def _generate_samples(self):
        for scenario in self.scenarios:
            # Extract static room features (normalized roughly)
            room_area = scenario["room_area"] / 50.0 # Normalize by max expected area
            aspect_ratio = scenario["room_aspect_ratio"] / 2.0
            num_doors = scenario["num_doors"] / 4.0
            num_windows = scenario["num_windows"] / 4.0
            num_furniture = scenario["num_furniture"] / 20.0
            
            # Base feature vector
            base_features = [room_area, aspect_ratio, num_doors, num_windows, num_furniture]
            
            # Prepare Geometry Objects
            room_poly_coords = scenario["original"]["room_polygon"]
            room_poly = create_room_polygon(room_poly_coords)
            doors = scenario["original"].get("doors", [])
            windows = scenario["original"].get("windows", [])
            furniture_items = scenario["original"]["selected_furniture"]
            
            # Initialize Evaluator for this room
            constraints = ConstraintChecker(room_poly, doors, windows)
            evaluator = FitnessEvaluator(room_poly, furniture_items, constraints)
            
            for _ in range(self.samples_per_room):
                # Randomize positions
                placed_items = []
                layout_features = [] # We need to encode the layout for the model
                
                # For simplicity in this surrogate model, we'll just use 
                # "average distance to center" and "average distance to walls" 
                # as layout features, plus the raw fitness score as label.
                # In a real advanced model, we'd input the full grid or graph.
                
                # Let's try to place them randomly within bounds
                # This is a simplified simulation
                min_x, min_y, max_x, max_y = room_poly.bounds
                
                current_layout_items = []
                
                for item in furniture_items:
                    # Random x, y, rotation
                    x = random.uniform(min_x, max_x)
                    y = random.uniform(min_y, max_y)
                    rotation = random.choice([0, 90, 180, 270]) if item["rotatable"] else 0
                    
                    # Create item with position
                    placed_item = item.copy()
                    placed_item["position"] = {"x": x, "y": y}
                    placed_item["rotation"] = rotation
                    current_layout_items.append(placed_item)
                
                # Calculate Fitness
                try:
                    score = evaluator.evaluate(room_poly, current_layout_items)
                except Exception:
                    score = -100 # Penalty for error
                
                # Normalize score (assuming range -100 to 100 roughly)
                normalized_score = max(-1.0, min(1.0, score / 100.0))
                
                # Add to dataset
                # Input: Base Features (5) + Random Noise (5) to simulate layout variance
                # In a real implementation, we would encode the actual positions.
                # For this demonstration, we are training the model to learn 
                # "This room type generally gets this score" + some noise.
                # TO DO: Implement full position encoding.
                
                # Simplified Feature Vector: 
                # [RoomArea, AspectRatio, NumDoors, NumWindows, NumFurniture, AvgX, AvgY, SpreadX, SpreadY]
                avg_x = sum(i["position"]["x"] for i in current_layout_items) / len(current_layout_items)
                avg_y = sum(i["position"]["y"] for i in current_layout_items) / len(current_layout_items)
                
                # Normalize positions by room dims
                width = max_x - min_x
                height = max_y - min_y
                norm_avg_x = avg_x / width if width > 0 else 0
                norm_avg_y = avg_y / height if height > 0 else 0
                
                features = base_features + [norm_avg_x, norm_avg_y]
                
                self.data.append(features)
                self.labels.append(normalized_score)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx], dtype=torch.float32), torch.tensor(self.labels[idx], dtype=torch.float32)

def train_model():
    print("="*50)
    print("STARTING MODEL TRAINING")
    print("="*50)
    
    # Paths
    base_dir = Path("processed_data")
    train_path = base_dir / "train.json"
    val_path = base_dir / "val.json"
    model_save_path = Path("backend/app/modules/interior/ml/models")
    model_save_path.mkdir(parents=True, exist_ok=True)
    
    # Hyperparameters
    BATCH_SIZE = 64
    LEARNING_RATE = 0.001
    EPOCHS = 20
    INPUT_SIZE = 7 # 5 base + 2 layout features
    
    # Load Data
    print("Loading Training Data...")
    train_dataset = InteriorDataset(train_path, samples_per_room=2) # 2 samples per room
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    print("Loading Validation Data...")
    val_dataset = InteriorDataset(val_path, samples_per_room=1)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    
    # Initialize Model
    model = InteriorFitnessModel(input_size=INPUT_SIZE)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"\nModel Architecture: {model}")
    print(f"Training on {len(train_dataset)} samples for {EPOCHS} epochs...")
    
    # Training Loop
    best_val_loss = float('inf')
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for inputs, targets in val_loader:
                outputs = model(inputs)
                loss = criterion(outputs.squeeze(), targets)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)
        
        print(f"Epoch [{epoch+1}/{EPOCHS}] Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")
        
        # Save Best Model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), model_save_path / "best_model.pth")
            # print("  Saved Best Model")
            
    print("="*50)
    print("TRAINING COMPLETE")
    print(f"Best Validation Loss: {best_val_loss:.4f}")
    print(f"Model saved to {model_save_path}/best_model.pth")
    print("="*50)

if __name__ == "__main__":
    train_model()
