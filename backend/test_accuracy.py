import urllib.request
import json

def test_context_matching():
    boundary = "----WebKitFormBoundaryAccuracyTest"
    sample_file = "c:/Users/Administrator/Desktop/AgriMind/backend/uploads/crop_sample.jpg"
    
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    tests = [
        {"batch_type": "Crops", "notes": "Healthy specimen routine inspection", "expected_issue": "Healthy Crop Specimen"},
        {"batch_type": "Crops", "notes": "Yellowing leaves and chlorosis at tips", "expected_issue": "Nitrogen (N) Deficiency"},
        {"batch_type": "Crops", "notes": "Whorl leaf holes and caterpillar damage", "expected_issue": "Fall Armyworm Damage"},
        {"batch_type": "Poultry", "notes": "Respiratory gasping, coughing and nasal discharge", "expected_issue": "Avian Infectious Bronchitis"},
        {"batch_type": "Livestock", "notes": "Udder quarter swelling and milk clots", "expected_issue": "Bovine Mastitis"}
    ]

    print("=== TESTING AI DIAGNOSIS MATCHING ACCURACY ===")
    for test in tests:
        body = bytearray()
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="batch_type"\r\n\r\n{test["batch_type"]}\r\n'.encode())
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="notes"\r\n\r\n{test["notes"]}\r\n'.encode())
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(b'Content-Disposition: form-data; name="file"; filename="sample.jpg"\r\nContent-Type: image/jpeg\r\n\r\n')
        body.extend(file_bytes)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())

        req = urllib.request.Request("http://127.0.0.1:8000/api/v1/diagnose", data=bytes(body))
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        
        res = urllib.request.urlopen(req)
        diag = json.loads(res.read().decode())
        issue = diag.get("detected_issue")
        print(f"Notes: '{test['notes']}' -> Detected: '{issue}' (Severity: {diag.get('severity')}, Confidence: {diag.get('confidence_score')}%)")

if __name__ == "__main__":
    test_context_matching()
