"""
Data Preprocessing Pipeline for Interior Optimization ML
- Loads all room scenarios from datasets
- Extracts features for ML training
- Creates train/validation/test splits
- Generates summary statistics
"""

import json
import os
import random
from pathlib import Path
from collections import defaultdict
import math

class DataPreprocessor:
    def __init__(self, datasets_dir="datasets/interior"):
        self.datasets_dir = datasets_dir
        self.all_data = []
        self.stats = defaultdict(int)
        
    def calculate_polygon_area(self, polygon):
        """Calculate area of polygon using Shoelace formula"""
        n = len(polygon)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += polygon[i][0] * polygon[j][1]
            area -= polygon[j][0] * polygon[i][1]
        return abs(area) / 2.0
    
    def get_polygon_bounds(self, polygon):
        """Get min/max x,y coordinates"""
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        return {
            "min_x": min(xs), "max_x": max(xs),
            "min_y": min(ys), "max_y": max(ys),
            "width": max(xs) - min(xs),
            "height": max(ys) - min(ys)
        }
    
    def extract_features(self, scenario):
        """Extract ML features from a room scenario"""
        # Room features
        polygon = scenario["room_polygon"]
        room_area = self.calculate_polygon_area(polygon)
        bounds = self.get_polygon_bounds(polygon)
        
        # Furniture features
        furniture = scenario.get("selected_furniture", [])
        total_furniture_area = sum(f["width"] * f["depth"] for f in furniture)
        
        # Categorize furniture by type
        furniture_by_category = defaultdict(int)
        for f in furniture:
            fid = f["furniture_id"]
            # Extract category from furniture_id (e.g., "bed" from "bed_queen_72x60")
            category = fid.split("_")[0]
            furniture_by_category[category] += 1
        
        features = {
            # IDs
            "room_id": scenario["room_id"],
            "room_type": scenario["room_type"],
            
            # Room geometry
            "room_area": room_area,
            "room_width": bounds["width"],
            "room_height": bounds["height"],
            "room_aspect_ratio": bounds["width"] / bounds["height"] if bounds["height"] > 0 else 1.0,
            "polygon_type": scenario.get("polygon_type", "rectangle"),
            "num_vertices": len(polygon),
            
            # Openings
            "num_doors": len(scenario.get("doors", [])),
            "num_windows": len(scenario.get("windows", [])),
            
            # Furniture
            "num_furniture": len(furniture),
            "total_furniture_area": total_furniture_area,
            "space_utilization": total_furniture_area / room_area if room_area > 0 else 0,
            "furniture_by_category": dict(furniture_by_category),
            
            # User goals
            "min_walkway": scenario.get("user_goals", {}).get("min_walkway", 0.7),
            "priority": scenario.get("user_goals", {}).get("priority", "space_efficiency"),
            
            # Property type
            "property_type": scenario.get("property_type", "house"),
            "size_category": scenario.get("size_category", "medium"),
            
            # Original data (for reconstruction)
            "original": scenario
        }
        
        return features
    
    def load_all_datasets(self):
        """Load all room scenarios from all room types"""
        room_types = ["bedroom", "living_room", "kitchen", "bathroom", "dining_room", "apartment"]
        
        print("Loading datasets...")
        for room_type in room_types:
            room_dir = Path(self.datasets_dir) / room_type
            if not room_dir.exists():
                continue
                
            json_files = list(room_dir.glob("*.json"))
            print(f"  {room_type}: {len(json_files)} files")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        scenario = json.load(f)
                        features = self.extract_features(scenario)
                        self.all_data.append(features)
                        
                        # Update stats
                        self.stats[f"total_{room_type}"] += 1
                        self.stats["total_scenarios"] += 1
                        
                except Exception as e:
                    print(f"    Error loading {json_file.name}: {e}")
        
        print(f"\nTotal loaded: {len(self.all_data)} scenarios")
        return self.all_data
    
    def create_splits(self, train_ratio=0.7, val_ratio=0.15):
        """Split data into train/val/test sets"""
        random.shuffle(self.all_data)
        
        n = len(self.all_data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        splits = {
            "train": self.all_data[:train_end],
            "val": self.all_data[train_end:val_end],
            "test": self.all_data[val_end:]
        }
        
        print(f"\nData splits:")
        print(f"  Train: {len(splits['train'])} ({train_ratio*100:.0f}%)")
        print(f"  Val: {len(splits['val'])} ({val_ratio*100:.0f}%)")
        print(f"  Test: {len(splits['test'])} ({(1-train_ratio-val_ratio)*100:.0f}%)")
        
        return splits
    
    def generate_statistics(self):
        """Generate summary statistics"""
        stats = {
            "total_scenarios": len(self.all_data),
            "by_room_type": defaultdict(int),
            "by_property_type": defaultdict(int),
            "by_polygon_type": defaultdict(int),
            "room_area": {"min": float('inf'), "max": 0, "avg": 0},
            "num_furniture": {"min": float('inf'), "max": 0, "avg": 0},
            "space_utilization": {"min": float('inf'), "max": 0, "avg": 0}
        }
        
        total_area = 0
        total_furniture = 0
        total_utilization = 0
        
        for data in self.all_data:
            # Count by type
            stats["by_room_type"][data["room_type"]] += 1
            stats["by_property_type"][data.get("property_type", "house")] += 1
            stats["by_polygon_type"][data.get("polygon_type", "rectangle")] += 1
            
            # Min/max/avg
            area = data["room_area"]
            num_furn = data["num_furniture"]
            utilization = data["space_utilization"]
            
            stats["room_area"]["min"] = min(stats["room_area"]["min"], area)
            stats["room_area"]["max"] = max(stats["room_area"]["max"], area)
            total_area += area
            
            stats["num_furniture"]["min"] = min(stats["num_furniture"]["min"], num_furn)
            stats["num_furniture"]["max"] = max(stats["num_furniture"]["max"], num_furn)
            total_furniture += num_furn
            
            stats["space_utilization"]["min"] = min(stats["space_utilization"]["min"], utilization)
            stats["space_utilization"]["max"] = max(stats["space_utilization"]["max"], utilization)
            total_utilization += utilization
        
        n = len(self.all_data)
        stats["room_area"]["avg"] = round(total_area / n, 2)
        stats["num_furniture"]["avg"] = round(total_furniture / n, 2)
        stats["space_utilization"]["avg"] = round(total_utilization / n, 3)
        
        # Convert defaultdicts to regular dicts
        stats["by_room_type"] = dict(stats["by_room_type"])
        stats["by_property_type"] = dict(stats["by_property_type"])
        stats["by_polygon_type"] = dict(stats["by_polygon_type"])
        
        return stats
    
    def save_processed_data(self, output_dir="processed_data"):
        """Save processed data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create splits
        splits = self.create_splits()
        
        # Save each split
        for split_name, split_data in splits.items():
            output_file = os.path.join(output_dir, f"{split_name}.json")
            with open(output_file, 'w') as f:
                json.dump(split_data, f, indent=2)
            print(f"  Saved {output_file}")
        
        # Save statistics
        stats = self.generate_statistics()
        stats_file = os.path.join(output_dir, "stats.json")
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"  Saved {stats_file}")
        
        return splits, stats

def main():
    print("=" * 60)
    print("Interior Optimization - Data Preprocessing")
    print("=" * 60)
    
    preprocessor = DataPreprocessor()
    
    # Load all datasets
    preprocessor.load_all_datasets()
    
    # Save processed data
    splits, stats = preprocessor.save_processed_data()
    
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total scenarios: {stats['total_scenarios']}")
    print(f"\nBy room type:")
    for room, count in stats['by_room_type'].items():
        print(f"  {room}: {count}")
    print(f"\nBy polygon type:")
    for poly, count in stats['by_polygon_type'].items():
        print(f"  {poly}: {count}")
    print(f"\nRoom area: {stats['room_area']['min']:.1f} - {stats['room_area']['max']:.1f} m² (avg: {stats['room_area']['avg']})")
    print(f"Furniture per room: {stats['num_furniture']['min']} - {stats['num_furniture']['max']} (avg: {stats['num_furniture']['avg']})")
    print(f"Space utilization: {stats['space_utilization']['min']:.1%} - {stats['space_utilization']['max']:.1%} (avg: {stats['space_utilization']['avg']:.1%})")
    print("=" * 60)
    print("\nPreprocessing complete! ✓")
    print("Next: Algorithm development")

if __name__ == "__main__":
    main()
