import json
import os
import sys
from pathlib import Path

def check_catalogs():
    print("\n[1/3] Checking Catalogs...")
    catalog_dir = Path("frontend/src/data/interior/catalogs")
    required_catalogs = [
        "bedroom_furniture_catalog.json",
        "living_room_furniture_catalog.json",
        "kitchen_furniture_catalog.json",
        "bathroom_furniture_catalog.json",
        "dining_room_furniture_catalog.json",
        "apartment_furniture_catalog.json"
    ]
    
    all_valid = True
    for cat in required_catalogs:
        path = catalog_dir / cat
        if not path.exists():
            print(f"  [MISSING] {cat}")
            all_valid = False
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                item_count = len(data.get("furniture", []))
                print(f"  [OK] {cat}: Valid JSON ({item_count} items)")
        except json.JSONDecodeError:
            print(f"  [INVALID JSON] {cat}")
            all_valid = False
            
    return all_valid

def check_datasets():
    print("\n[2/3] Checking Datasets...")
    dataset_dir = Path("datasets")
    room_types = ["bedroom", "living_room", "kitchen", "bathroom", "dining_room", "apartment"]
    
    all_valid = True
    total_files = 0
    
    for room in room_types:
        path = dataset_dir / room
        if not path.exists():
            print(f"  [MISSING DIR] {room}")
            all_valid = False
            continue
            
        count = len(list(path.glob("*.json")))
        total_files += count
        if count == 0:
            print(f"  [EMPTY] {room}")
            all_valid = False
        else:
            print(f"  [OK] {room}: {count} files")
            
    print(f"  Total Dataset Files: {total_files}")
    return all_valid and total_files > 0

def check_processed_data():
    print("\n[3/3] Checking Processed Data...")
    processed_dir = Path("processed_data")
    required_files = ["train.json", "val.json", "test.json", "stats.json"]
    
    all_valid = True
    for file in required_files:
        path = processed_dir / file
        if not path.exists():
            print(f"  [MISSING] {file}")
            all_valid = False
            continue
            
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  [OK] {file}: {size_mb:.2f} MB")
        
    if (processed_dir / "stats.json").exists():
        with open(processed_dir / "stats.json", 'r', encoding='utf-8') as f:
            stats = json.load(f)
            print("\n  --- Data Distribution ---")
            for room, count in stats.get("by_room_type", {}).items():
                print(f"  - {room}: {count}")
                
    return all_valid

def main():
    print("="*50)
    print("SYSTEM READINESS CHECK")
    print("="*50)
    
    catalogs_ok = check_catalogs()
    datasets_ok = check_datasets()
    processed_ok = check_processed_data()
    
    print("\n" + "="*50)
    if catalogs_ok and datasets_ok and processed_ok:
        print("RESULT: [READY] SYSTEM IS READY FOR TRAINING")
    else:
        print("RESULT: [FAIL] ISSUES DETECTED")
    print("="*50)

if __name__ == "__main__":
    main()
