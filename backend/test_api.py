import urllib.request
import json
import os

def test_api():
    print("=== Testing GET /api/v1/health ===")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health")
    print("Health response:", json.loads(res.read().decode()))

    print("\n=== Testing GET /api/v1/stats ===")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/stats")
    print("Stats response:", json.loads(res.read().decode()))

    print("\n=== Testing GET /api/v1/batches ===")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/batches")
    batches = json.loads(res.read().decode())
    print(f"Retrieved {len(batches)} batches:")
    for b in batches:
        print(f" - {b['name']} ({b['batch_type']}): {b['current_quantity']}/{b['initial_quantity']} units")

    print("\n=== Testing POST /api/v1/diagnose (Multimodal AI Vision Upload) ===")
    boundary = "----WebKitFormBoundaryAgriMindTest"
    sample_file = "c:/Users/Administrator/Desktop/AgriMind/backend/uploads/poultry_sample.jpg"
    
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="batch_type"\r\n\r\nPoultry\r\n')
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="notes"\r\n\r\nObserved ruffled feathers and lethargy\r\n')
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="file"; filename="poultry_sample.jpg"\r\nContent-Type: image/jpeg\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/diagnose", data=bytes(body))
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    res = urllib.request.urlopen(req)
    diag = json.loads(res.read().decode())
    print("AI Diagnostic Output:")
    print("  Disease/Issue:", diag.get("detected_issue"))
    print("  Severity Level:", diag.get("severity"))
    print("  Confidence:", diag.get("confidence_score"), "%")
    print("  Immediate Actions:", diag.get("treatment_plan", {}).get("immediate_actions"))
    print("  Resource Adjustments:", diag.get("treatment_plan", {}).get("resource_adjustments"))
    
    print("\nALL ENDPOINTS TESTED AND OPERATIONAL!")

if __name__ == "__main__":
    test_api()

