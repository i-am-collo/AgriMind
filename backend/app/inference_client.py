"""
AgriMind — Inference Client Abstraction Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides a clean interface between the AI engine and the underlying
vision-language model (VLM) inference backend.

Supported backends
------------------
* VLMInferenceClient  — OpenAI-compatible `/v1/chat/completions` endpoint
                        served by vLLM or NVIDIA NIM.
                        Structured output is enforced via
                        ``extra_body={"guided_json": <schema>}`` (vLLM ≥0.4)
                        or the standard ``response_format`` field (NIM / newer
                        vLLM that adopted the OpenAI structured-outputs spec).

Fallback behaviour
------------------
If the endpoint is unreachable or returns an error the caller receives an
``InferenceError`` exception; the caller is responsible for activating the
keyword-based fallback engine (preserved in ai_engine.py).
"""

from __future__ import annotations

import base64
import json
import logging
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

import httpx
from PIL import Image

from app.config import settings
from app.models import DiagnosticResult, ResourceAdjustments

logger = logging.getLogger("agrimind.inference")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class InferenceError(RuntimeError):
    """Raised when the remote VLM endpoint fails in any way."""


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class InferenceClient(ABC):
    """Public contract every inference backend must satisfy."""

    @abstractmethod
    async def diagnose_image(
        self,
        image: Image.Image,
        category: str,
        notes: str | None,
    ) -> DiagnosticResult:
        """
        Run visual diagnostics on *image* and return a structured result.

        Parameters
        ----------
        image:
            PIL Image already loaded and in RGB mode.
        category:
            One of ``"Crops"``, ``"Livestock"``, or ``"Poultry"``.
        notes:
            Free-text field observations supplied by the farmer/extension
            worker. May be ``None`` or an empty string.

        Returns
        -------
        DiagnosticResult
            Validated Pydantic model instance.

        Raises
        ------
        InferenceError
            On any connectivity, timeout, or schema validation failure.
        """


# ---------------------------------------------------------------------------
# Concrete VLM client (vLLM / NIM OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------

_AGRIMIND_SYSTEM_PROMPT = """\
You are AgriMind AI, the AI-Powered Smart Agricultural Resource Engine.
Your mission is to provide accurate, reliable, hyper-local agronomic diagnostics
to farmers and extension workers.

TARGET CATEGORY: {category}

CRITICAL EXECUTION RULES:
1. STRICT VISUAL EVIDENCE: Base your analysis only on what is visible in the image
   combined with the field observations provided. Do not fabricate dosages or steps.
2. HYPER-LOCAL ADVICE: Tailor recommendations to the microclimate and regional
   constraints implied by the notes.
3. SAFETY & DOSAGE PRECISION: When prescribing treatments, specify exact proportions,
   water-mix ratios, and safety precautions (FAO/extension-guide standards).
4. ACCESSIBLE LANGUAGE: Short bullet points suitable for mobile or voice TTS.
5. OUTPUT FORMAT: You MUST respond with ONLY valid JSON conforming exactly to the
   DiagnosticResult schema provided. No prose, no markdown fences — raw JSON only.
"""

_USER_PROMPT_TEMPLATE = """\
Analyse this {category} image for disease, pest, nutritional deficiency, or
health confirmation.

Field observations / notes: {notes}

Return ONLY a JSON object matching the schema. Every field is required.
"""


def _pil_to_base64_url(image: Image.Image) -> str:
    """Encode a PIL image as a data-URI compatible base64 string."""
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


class VLMInferenceClient(InferenceClient):
    """
    Calls a self-hosted vision-language model through an OpenAI-compatible
    ``/v1/chat/completions`` endpoint (vLLM ≥ 0.4 or NVIDIA NIM).

    Configuration is read from :class:`app.config.Settings`:

    * ``INFERENCE_ENDPOINT_URL``  — base URL, e.g. ``http://10.0.0.1:8000``
    * ``INFERENCE_MODEL_NAME``    — HuggingFace model ID as accepted by vLLM
    * ``INFERENCE_TIMEOUT_SECONDS``
    * ``INFERENCE_MAX_RETRIES``
    """

    def __init__(self) -> None:
        self._endpoint = settings.INFERENCE_ENDPOINT_URL.rstrip("/")
        self._model = settings.INFERENCE_MODEL_NAME
        self._timeout = float(settings.INFERENCE_TIMEOUT_SECONDS)
        self._max_retries = int(settings.INFERENCE_MAX_RETRIES)
        # Pre-build the JSON schema once — it never changes at runtime.
        self._json_schema: dict[str, Any] = DiagnosticResult.model_json_schema()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def diagnose_image(
        self,
        image: Image.Image,
        category: str,
        notes: str | None,
    ) -> DiagnosticResult:
        notes = notes or "Routine visual health inspection"
        image_url = _pil_to_base64_url(image)

        system_content = _AGRIMIND_SYSTEM_PROMPT.format(category=category)
        user_content = _USER_PROMPT_TEMPLATE.format(
            category=category,
            notes=notes,
        )

        payload = self._build_payload(system_content, user_content, image_url)
        raw_json = await self._post_with_retry(payload)
        return self._parse_response(raw_json)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        system_content: str,
        user_content: str,
        image_url: str,
    ) -> dict[str, Any]:
        """
        Construct the chat-completions request body.

        vLLM structured output is enforced through ``extra_body``
        (``guided_json`` for vLLM < 0.6, ``structured_outputs`` for ≥ 0.6).
        We include both keys so the server picks whichever it supports.
        NIM endpoints honour the standard ``response_format`` field instead.
        """
        return {
            "model": self._model,
            "temperature": 0.05,
            "max_tokens": 1024,
            "messages": [
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                        {"type": "text", "text": user_content},
                    ],
                },
            ],
            # vLLM ≥ 0.4 guided decoding (both keys for broad compatibility)
            "guided_json": self._json_schema,
            "extra_body": {
                "guided_json": self._json_schema,
                "structured_outputs": {"json": self._json_schema},
            },
            # NIM / OpenAI structured output standard
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "DiagnosticResult",
                    "schema": self._json_schema,
                    "strict": True,
                },
            },
        }

    async def _post_with_retry(self, payload: dict[str, Any]) -> str:
        """POST to the completions endpoint; retries on transient errors."""
        url = f"{self._endpoint}/v1/chat/completions"
        last_exc: Exception | None = None

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(1, self._max_retries + 1):
                try:
                    logger.info(
                        "[VLMClient] POST %s — model=%s attempt=%d/%d",
                        url,
                        self._model,
                        attempt,
                        self._max_retries,
                    )
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    return resp.text
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    last_exc = exc
                    logger.warning(
                        "[VLMClient] Transient error on attempt %d: %s",
                        attempt,
                        exc,
                    )
                except httpx.HTTPStatusError as exc:
                    # 4xx errors are not transient — fail fast
                    raise InferenceError(
                        f"VLM endpoint returned HTTP {exc.response.status_code}: "
                        f"{exc.response.text[:300]}"
                    ) from exc

        raise InferenceError(
            f"VLM endpoint unreachable after {self._max_retries} attempts: {last_exc}"
        )

    @staticmethod
    def _parse_response(raw: str) -> DiagnosticResult:
        """Extract content from the completions envelope and validate schema."""
        try:
            envelope = json.loads(raw)
            content: str = envelope["choices"][0]["message"]["content"]
            # Strip optional markdown code fences the model may add anyway
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content.strip())
            return DiagnosticResult(**data)
        except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            raise InferenceError(
                f"Failed to parse VLM response into DiagnosticResult: {exc}\n"
                f"Raw response (first 500 chars): {raw[:500]}"
            ) from exc


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def get_inference_client() -> VLMInferenceClient:
    """Return a ready-to-use :class:`VLMInferenceClient` instance."""
    return VLMInferenceClient()
