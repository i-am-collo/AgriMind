# AgriMind — NVIDIA Brev GPU Deployment Guide

This directory contains the deployment configuration for the AgriMind
self-hosted vision-language model (VLM) inference server.

| Item | Value |
|---|---|
| **Model** | `Qwen/Qwen2-VL-7B-Instruct` |
| **Runtime** | vLLM OpenAI-compatible server |
| **Primary GPU** | NVIDIA L4 24 GB |
| **Fallback GPU** | NVIDIA A10G 24 GB / A100 40 GB |
| **Exposed port** | `8000` (OpenAI-compatible `/v1/*`) |

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Brev account | Sign up at [brev.nvidia.com](https://brev.nvidia.com) |
| HuggingFace token | `HF_TOKEN` with read access to `Qwen/Qwen2-VL-7B-Instruct` — obtain at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| GitHub repo | This project must be in a GitHub repository Brev can read |

---

## Step-by-Step Provisioning

### 1 — Add your HuggingFace token as a Brev Secret

1. Log in to [brev.nvidia.com](https://brev.nvidia.com).
2. Navigate to **Secrets** in the left sidebar.
3. Create a new secret named **`HF_TOKEN`** with your HuggingFace access token as the value.
4. Note the secret name — you will bind it in the Launchable below.

---

### 2 — Create the Launchable

1. In the Brev dashboard, click **+ New Launchable**.
2. **Source:** Select _"I have code files in a GitHub repository"_.
   - Enter your AgriMind repository URL.
   - Branch: `main`
3. **Environment:** Choose _"With container(s)"_ → _"Docker Compose"_.
4. **Compose file path:** `deploy/brev/docker-compose.yaml`
5. **Secrets:** Bind the `HF_TOKEN` secret created in Step 1 to the
   `HF_TOKEN` environment variable.
6. **GPU:** Select **L4 24 GB** (preferred).
   - If unavailable, select **A10G 24 GB** or **A100 40 GB**.
7. **Name** the Launchable `agrimind-vlm` and click **Launch**.

> [!NOTE]
> The first launch downloads ~15 GB of model weights.
> This takes 5–15 minutes depending on network speed.
> Subsequent launches use the cached weights from the `model_cache` volume.

---

### 3 — Get the inference endpoint URL

After the container passes its health check:

1. In the Launchable dashboard, click **Ports**.
2. Copy the public tunnel URL for port `8000`.
   It looks like: `https://agrimind-vlm-xxxxxxxx.brevlab.com`
3. Verify it is up: open `<tunnel-url>/v1/models` in a browser.
   You should see `Qwen/Qwen2-VL-7B-Instruct` in the model list.

---

### 4 — Configure the AgriMind backend

In your local AgriMind project, create / edit `.env`:

```env
INFERENCE_ENDPOINT_URL=https://agrimind-vlm-xxxxxxxx.brevlab.com
INFERENCE_MODEL_NAME=Qwen/Qwen2-VL-7B-Instruct
INFERENCE_TIMEOUT_SECONDS=120
INFERENCE_MAX_RETRIES=3
```

Then restart the backend:

```powershell
cd c:\Users\Administrator\Desktop\AgriMind\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Upload a diagnostic image through the UI. The backend logs will show:

```
[AI Engine] VLM diagnosis complete: <issue> (xx.x%)
```

---

## Architecture

```
┌───────────────────────────┐        ┌─────────────────────────────────┐
│  AgriMind Backend          │        │  NVIDIA Brev GPU Instance        │
│  FastAPI / port 8001       │        │                                 │
│                            │  HTTPS │  ┌──────────────────────────┐   │
│  POST /api/v1/diagnose ────┼──────►─┼──► vLLM OpenAI-compatible    │   │
│                            │        │  │  server  :8000            │   │
│  inference_client.py       │◄───────┼──│  Qwen2-VL-7B-Instruct    │   │
│  (VLMInferenceClient)      │  JSON  │  │  L4 / A10G GPU           │   │
└───────────────────────────┘        │  └──────────────────────────┘   │
                                     └─────────────────────────────────┘
```

---

## Model Alternatives

If `Qwen/Qwen2-VL-7B-Instruct` is unavailable, edit `docker-compose.yaml`
and your `.env` to use one of these drop-in replacements:

| Model | Memory | `--model` value |
|---|---|---|
| InternVL2-8B | ~18 GB | `OpenGVLab/InternVL2-8B` |
| LLaVA-NeXT (Llama-3.1-8B) | ~18 GB | `lmms-lab/llama3-llava-next-8b` |
| Qwen2.5-VL-7B-Instruct | ~16 GB | `Qwen/Qwen2.5-VL-7B-Instruct` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Health check never passes | Model download still in progress | Wait 10–15 min; check container logs |
| `CUDA out of memory` | GPU VRAM too small | Lower `--gpu-memory-utilization` to `0.85` or pick A100 |
| `InferenceError: HTTP 422` | Request format mismatch | Check vLLM version; update `INFERENCE_MODEL_NAME` to match exactly |
| Diagnosis always hits fallback | `INFERENCE_ENDPOINT_URL` not set / wrong | Verify `.env` value matches Brev tunnel URL |
| Slow responses (>60 s) | Cold start or long context | Increase `INFERENCE_TIMEOUT_SECONDS` to `180` |
