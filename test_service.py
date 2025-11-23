"""Test script for MLX-VLM Receipt Scanner Service"""
import requests
import sys
import json

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_extract(image_path):
    """Test extract endpoint with an image"""
    print(f"\nTesting extract endpoint with image: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post("http://localhost:8000/extract", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except FileNotFoundError:
        print(f"Error: Image file not found: {image_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_models():
    """Test models endpoint"""
    print("\nTesting models endpoint...")
    try:
        response = requests.get("http://localhost:8000/models")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MLX-VLM Receipt Scanner Service - Test Suite")
    print("=" * 60)
    
    # Test health
    health_ok = test_health()
    
    # Test models
    models_ok = test_models()
    
    # Test extract if image path provided
    extract_ok = True
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        extract_ok = test_extract(image_path)
    else:
        print("\nSkipping extract test (no image path provided)")
        print("Usage: python test_service.py <path_to_receipt_image>")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"  Models List:  {'✅ PASS' if models_ok else '❌ FAIL'}")
    if len(sys.argv) > 1:
        print(f"  Extract Data: {'✅ PASS' if extract_ok else '❌ FAIL'}")
    print("=" * 60)
    
    sys.exit(0 if (health_ok and models_ok and extract_ok) else 1)
