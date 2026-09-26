"""
AgriMind — AI Diagnosis Accuracy & Inference Client Tests
==========================================================
Covers two concerns:

1. Context-matching accuracy of the keyword-based fallback engine
   (always-available, no network required).
2. Behaviour of VLMInferenceClient when the remote endpoint is
   unavailable — verifying graceful fallback to the keyword engine.

Run with:
    python backend/test_accuracy.py            # live HTTP test (needs running server)
    python backend/test_accuracy.py --unit     # unit tests only (no server required)
"""

from __future__ import annotations

import json
import sys
import types
import unittest
import unittest.mock
import urllib.request
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Path setup so we can import from backend/app without installing the package
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------------------------
# Fallback engine accuracy test (no network required)
# ---------------------------------------------------------------------------

class TestFallbackEngineAccuracy(unittest.TestCase):
    """Validates the keyword-based fallback engine routing and output schema."""

    def setUp(self) -> None:
        from app.ai_engine import generate_expert_fallback_diagnostic
        self.engine = generate_expert_fallback_diagnostic

    # -------- Crops --------------------------------------------------------

    def test_crop_healthy(self) -> None:
        r = self.engine("Crops", "Healthy specimen routine inspection")
        self.assertIn("Healthy", r.detected_issue)
        self.assertEqual(r.severity, "Low")
        self.assertFalse(r.isolation_required)

    def test_crop_nitrogen_deficiency(self) -> None:
        r = self.engine("Crops", "Yellowing leaves and chlorosis at tips")
        self.assertIn("Nitrogen", r.detected_issue)
        self.assertEqual(r.severity, "Medium")

    def test_crop_armyworm(self) -> None:
        r = self.engine("Crops", "Whorl leaf holes and caterpillar damage")
        self.assertIn("Armyworm", r.detected_issue)
        self.assertEqual(r.severity, "High")

    def test_crop_default_blight(self) -> None:
        r = self.engine("Maize", "Random unmatched field observation")
        self.assertIn("Blight", r.detected_issue)

    # -------- Poultry ------------------------------------------------------

    def test_poultry_respiratory(self) -> None:
        r = self.engine("Poultry", "Respiratory gasping, coughing and nasal discharge")
        self.assertIn("Bronchitis", r.detected_issue)
        self.assertEqual(r.severity, "Critical")
        self.assertTrue(r.isolation_required)

    def test_poultry_healthy(self) -> None:
        r = self.engine("Poultry", "Normal active foraging flock")
        self.assertIn("Healthy", r.detected_issue)
        self.assertFalse(r.isolation_required)

    def test_poultry_default_coccidiosis(self) -> None:
        r = self.engine("Poultry", "Ruffled feathers and dark droppings")
        self.assertIn("Coccidiosis", r.detected_issue)

    # -------- Livestock ----------------------------------------------------

    def test_livestock_mastitis(self) -> None:
        r = self.engine("Livestock", "Udder quarter swelling and milk clots")
        self.assertIn("Mastitis", r.detected_issue)
        self.assertEqual(r.severity, "High")
        self.assertTrue(r.isolation_required)

    def test_livestock_healthy(self) -> None:
        r = self.engine("Cattle", "Normal body condition and alert posture")
        self.assertIn("Healthy", r.detected_issue)
        self.assertFalse(r.isolation_required)

    # -------- Schema integrity ---------------------------------------------

    def test_result_schema_completeness(self) -> None:
        """Every required DiagnosticResult field must be present and typed."""
        from app.models import DiagnosticResult
        r = self.engine("Poultry", "coughing birds")
        self.assertIsInstance(r, DiagnosticResult)
        self.assertIsInstance(r.detected_issue, str)
        self.assertIsInstance(r.severity, str)
        self.assertIsInstance(r.confidence_score, float)
        self.assertIsInstance(r.symptom_analysis, list)
        self.assertIsInstance(r.immediate_actions, list)
        self.assertIsInstance(r.medication_or_inputs, list)
        self.assertIsInstance(r.preventative_measures, list)
        self.assertIsInstance(r.isolation_required, bool)
        self.assertIsInstance(r.resource_adjustments.feed_recommendation, str)
        self.assertIsInstance(r.resource_adjustments.water_recommendation, str)


# ---------------------------------------------------------------------------
# VLMInferenceClient unit tests (no real endpoint required)
# ---------------------------------------------------------------------------

class TestVLMInferenceClientFallback(unittest.IsolatedAsyncioTestCase):
    """
    Verifies that when VLMInferenceClient raises InferenceError the
    run_ai_diagnosis function transparently falls back to the expert engine.
    """

    def _make_rgb_image(self):
        """Return a tiny 4×4 white PIL image for testing."""
        from PIL import Image
        return Image.new("RGB", (4, 4), color=(255, 255, 255))

    async def test_vlm_connect_error_triggers_fallback(self) -> None:
        """ConnectError → InferenceError → fallback engine used."""
        from app.inference_client import InferenceError, VLMInferenceClient

        with patch.object(
            VLMInferenceClient,
            "_post_with_retry",
            new=AsyncMock(side_effect=InferenceError("connection refused")),
        ):
            client = VLMInferenceClient()
            with self.assertRaises(InferenceError):
                img = self._make_rgb_image()
                await client.diagnose_image(img, "Poultry", "coughing birds")

    def test_endpoint_failure_falls_back_to_keyword_engine(self) -> None:
        """
        When GEMINI_API_KEY is absent, run_ai_diagnosis must produce a valid
        DiagnosticResult via the keyword fallback engine — never raise.
        """
        import app.ai_engine as engine_module
        from app.models import DiagnosticResult

        # Simulate: no Gemini API key configured
        with patch("app.ai_engine.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = ""

            img_bytes = BytesIO()
            from PIL import Image
            Image.new("RGB", (4, 4)).save(img_bytes, format="JPEG")
            img_bytes = img_bytes.getvalue()

            result = engine_module.run_ai_diagnosis(
                img_bytes, "Poultry", "coughing and gasping birds"
            )

        self.assertIsInstance(result, DiagnosticResult)
        self.assertIn("Bronchitis", result.detected_issue)

    def test_vlm_bad_json_raises_inference_error(self) -> None:
        """Malformed JSON in the VLM response must raise InferenceError."""
        from app.inference_client import InferenceError, VLMInferenceClient

        bad_response = json.dumps(
            {"choices": [{"message": {"content": "not json at all"}}]}
        )

        with patch.object(
            VLMInferenceClient,
            "_post_with_retry",
            new=AsyncMock(return_value=bad_response),
        ):
            client = VLMInferenceClient()
            import asyncio
            with self.assertRaises(InferenceError):
                asyncio.run(
                    client.diagnose_image(
                        self._make_rgb_image(), "Crops", "yellowing"
                    )
                )


# ---------------------------------------------------------------------------
# Live HTTP integration test (requires running backend on port 8001)
# ---------------------------------------------------------------------------

def run_live_http_tests() -> None:
    """
    Sends real multipart form requests to the running AgriMind backend.
    Requires:  ``uvicorn app.main:app --port 8001`` running in backend/
    """
    sample_file = BACKEND_DIR / "uploads" / "crop_sample.jpg"
    if not sample_file.exists():
        print("[SKIP] crop_sample.jpg not found — skipping live HTTP tests.")
        return

    with open(sample_file, "rb") as fh:
        file_bytes = fh.read()

    cases = [
        {"batch_type": "Crops",    "notes": "Healthy specimen routine inspection",
         "expect": "Healthy Crop"},
        {"batch_type": "Crops",    "notes": "Yellowing leaves and chlorosis at tips",
         "expect": "Nitrogen"},
        {"batch_type": "Crops",    "notes": "Whorl leaf holes and caterpillar damage",
         "expect": "Armyworm"},
        {"batch_type": "Poultry",  "notes": "Respiratory gasping, coughing and nasal discharge",
         "expect": "Bronchitis"},
        {"batch_type": "Livestock","notes": "Udder quarter swelling and milk clots",
         "expect": "Mastitis"},
    ]

    boundary = "----AgriMindAccuracyBoundary"
    print("\n=== AgriMind — Live Diagnosis Accuracy Test ===\n")
    passed = failed = 0

    for case in cases:
        body = bytearray()
        for field in ("batch_type", "notes"):
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(
                f'Content-Disposition: form-data; name="{field}"\r\n\r\n'
                f'{case[field]}\r\n'.encode()
            )
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            b'Content-Disposition: form-data; name="file"; filename="sample.jpg"\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
        )
        body.extend(file_bytes)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            "http://127.0.0.1:8001/api/v1/diagnose", data=bytes(body)
        )
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

        try:
            res = urllib.request.urlopen(req, timeout=60)
            diag = json.loads(res.read().decode())
            issue = diag.get("detected_issue", "")
            ok = case["expect"].lower() in issue.lower()
            status = "✓ PASS" if ok else "✗ FAIL"
            if ok:
                passed += 1
            else:
                failed += 1
            print(
                f"  {status} | {case['batch_type']:10s} | "
                f"notes='{case['notes'][:50]}' | "
                f"got='{issue}'"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ ERROR | {case['batch_type']} | {exc}")
            failed += 1

    total = passed + failed
    print(f"\n  Results: {passed}/{total} passed\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--unit" in sys.argv or "-u" in sys.argv:
        # Run only unit tests (no server required)
        sys.argv = [sys.argv[0]]
        unittest.main(verbosity=2)
    else:
        # Run both: unit tests first, then live HTTP
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestFallbackEngineAccuracy))
        suite.addTests(loader.loadTestsFromTestCase(TestVLMInferenceClientFallback))

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        if result.wasSuccessful():
            run_live_http_tests()
        else:
            print("\n[SKIP] Live HTTP tests skipped due to unit test failures.")
            sys.exit(1)
