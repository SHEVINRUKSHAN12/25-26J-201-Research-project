import requests
import json

def test_low_space_optimization():
    url = "http://127.0.0.1:8000/api/v1/interior/optimize"
    
    # 1. Define Small Room (3m x 3m)
    room_polygon = [
        [0, 0],
        [3.0, 0],
        [3.0, 3.0],
        [0, 3.0]
    ]
    
    # 2. Define Large Furniture (Crowded)
    furniture_items = [
        {"id": "bed_king", "width": 1.8, "depth": 2.0, "category": "bedroom", "rotatable": True},
        {"id": "wardrobe_large", "width": 1.5, "depth": 0.6, "category": "bedroom", "rotatable": True},
        {"id": "desk_study", "width": 1.2, "depth": 0.6, "category": "bedroom", "rotatable": True},
        {"id": "chair_office", "width": 0.5, "depth": 0.5, "category": "bedroom", "rotatable": True}
    ]
    
    payload = {
        "room_polygon": room_polygon,
        "furniture_items": furniture_items,
        "constraints": {}
    }
    
    print(f"Testing Low Space Scenario (3x3m Room)...")
    print(f"Items: King Bed, Wardrobe, Desk, Chair")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ OPTIMIZATION SUCCESS!")
            print(f"Fitness Score: {data.get('fitness'):.2f}")
            print(f"Quality Score: {data.get('score_percentage')}%")
            
            print("\nOptimized Layout:")
            for item in data.get('layout', []):
                print(f" - {item['id']}: x={item['x']}, y={item['y']}, rot={item['rotation']}")
                
            if data.get('score_percentage') > 50:
                print("\nResult: The AI found a valid layout despite the small space!")
            else:
                print("\nResult: The space was too tight, resulting in a low score (expected).")
                
        else:
            print(f"❌ FAILURE: API returned {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_low_space_optimization()
