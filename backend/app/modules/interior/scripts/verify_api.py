import requests
import json

def verify_api():
    url = "http://127.0.0.1:8000/api/v1/interior/optimize"
    
    payload = {
        "room_polygon": [[0,0], [5,0], [5,5], [0,5]],
        "furniture_items": [
            {"id": "bed_1", "width": 2.0, "depth": 2.0, "category": "bedroom", "rotatable": True},
            {"id": "table_1", "width": 1.0, "depth": 1.0, "category": "bedroom", "rotatable": True}
        ],
        "constraints": {}
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: API returned 200 OK")
            print(f"   Fitness: {data.get('fitness')}")
            print(f"   Score: {data.get('score_percentage')}%")
            print(f"   Items Placed: {len(data.get('layout', []))}")
            
            # Verify IDs
            sent_ids = {item['id'] for item in payload['furniture_items']}
            received_ids = {item['id'] for item in data.get('layout', [])}
            
            print(f"   Sent IDs: {sent_ids}")
            print(f"   Received IDs: {received_ids}")
            
            if sent_ids == received_ids:
                print("✅ ID MATCH: IDs preserved correctly.")
            else:
                print("❌ ID MISMATCH: Backend returned different IDs!")
        else:
            print(f"❌ FAILURE: API returned {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    verify_api()
