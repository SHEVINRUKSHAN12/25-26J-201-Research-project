#!/usr/bin/env python3
"""
Simple API Test Script for Vastu System
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_yolo_analysis():
    """Test the YOLO analysis endpoint"""
    print("\n🔍 Testing YOLO Analysis Endpoint...")

    # Sample YOLO detection data
    test_data = {
        "yolo_detections": [
            {
                "class_id": 0,  # bedroom
                "confidence": 0.92,
                "bbox": [50, 50, 150, 150]
            },
            {
                "class_id": 1,  # kitchen
                "confidence": 0.88,
                "bbox": [200, 50, 300, 150]
            },
            {
                "class_id": 2,  # toilet
                "confidence": 0.85,
                "bbox": [50, 200, 150, 300]
            }
        ],
        "compass": {
            "rotation_angle": 0.0
        },
        "floor_width": 400,
        "floor_height": 400
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze/yolo",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ YOLO analysis successful!")
            print(f"   📊 Compliance Score: {data.get('compliance_score', 'N/A')}%")
            print(f"   📋 Rules Breakdown: {len(data.get('rule_breakdown', []))} rules")
            if 'explanation_reference_id' in data:
                print(f"   📝 Explanation ID: {data['explanation_reference_id']}")
            return True
        else:
            print(f"❌ YOLO analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ YOLO analysis error: {e}")
        return False

def test_explanation():
    """Test the explanation endpoint"""
    print("\n🔍 Testing Explanation Endpoint...")

    # First do an analysis to get an explanation ID
    test_data = {
        "yolo_detections": [
            {
                "class_id": 0,
                "confidence": 0.9,
                "bbox": [10, 10, 50, 50]
            }
        ],
        "compass": {"rotation_angle": 0.0},
        "floor_width": 100,
        "floor_height": 100
    }

    try:
        # Get analysis first
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze/yolo",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            analysis_data = response.json()
            explanation_id = analysis_data.get('explanation_reference_id')

            if explanation_id:
                # Now test explanation
                exp_response = requests.get(f"{BASE_URL}/api/v1/explain/{explanation_id}")
                if exp_response.status_code == 200:
                    exp_data = exp_response.json()
                    print("✅ Explanation retrieval successful!")
                    print(f"   📝 Explanation: {exp_data.get('explanation', '')[:100]}...")
                    return True
                else:
                    print(f"❌ Explanation retrieval failed: {exp_response.status_code}")
                    return False
            else:
                print("❌ No explanation ID in analysis response")
                return False
        else:
            print(f"❌ Analysis failed for explanation test: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Explanation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VASTU API FUNCTIONALITY TEST")
    print("=" * 50)

    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)

    tests = [
        ("Health Check", test_health),
        ("YOLO Analysis", test_yolo_analysis),
        ("Explanation", test_explanation)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Your Vastu API is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()