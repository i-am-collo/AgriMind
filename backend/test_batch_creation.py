import urllib.request
import json

def test_batch_creation():
    url = "http://127.0.0.1:8000/api/v1/batches"
    payload = {
        "name": "Test Broiler Flock E",
        "batch_type": "Poultry",
        "initial_quantity": 650,
        "current_quantity": 650,
        "status": "Active"
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    print("=== Testing POST /api/v1/batches ===")
    res = urllib.request.urlopen(req)
    result = json.loads(res.read().decode())
    print("Batch Created Successfully:")
    print("  ID:", result.get("id"))
    print("  Name:", result.get("name"))
    print("  Batch Type:", result.get("batch_type"))
    print("  Initial Quantity:", result.get("initial_quantity"))
    print("  Current Quantity:", result.get("current_quantity"))
    print("  Status:", result.get("status"))

    print("\n=== Verifying GET /api/v1/batches ===")
    res_list = urllib.request.urlopen(url)
    batches = json.loads(res_list.read().decode())
    found = any(b['id'] == result['id'] for b in batches)
    print(f"Newly created batch found in database list: {found} (Total Batches: {len(batches)})")

if __name__ == "__main__":
    test_batch_creation()
