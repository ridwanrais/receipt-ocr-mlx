# Model Selection Guide

## Switching Models

You can easily switch between different vision models by editing the `.env` file:

```bash
# Edit .env file
MODEL_NAME=<model-name>
```

Then restart the service:
```bash
# Kill existing service
lsof -ti:8000 | xargs kill -9

# Restart
make run
```

---

## Available Models

### 1. Qwen2-VL-2B-Instruct (Default)
```bash
MODEL_NAME=qwen/Qwen2-VL-2B-Instruct
```
- **Size:** ~2-4 GB
- **Speed:** Very fast (2-4s)
- **Accuracy:** Good for simple receipts
- **RAM:** ~4-6 GB
- **Best for:** Quick testing, simple receipts

### 2. Qwen2-VL-7B-Instruct (Recommended)
```bash
MODEL_NAME=qwen/Qwen2-VL-7B-Instruct
```
- **Size:** ~8 GB
- **Speed:** Moderate (4-8s)
- **Accuracy:** Better OCR, less hallucination
- **RAM:** ~8-12 GB
- **Best for:** Production, complex invoices

### 3. LLaVA 1.5 7B
```bash
MODEL_NAME=llava-hf/llava-1.5-7b-hf
```
- **Size:** ~7 GB
- **Speed:** Moderate (5-10s)
- **Accuracy:** Good general vision understanding
- **RAM:** ~8-10 GB
- **Best for:** Alternative if Qwen doesn't work well

---

## Model Comparison

| Model | Size | Speed | Accuracy | Hallucination | RAM |
|-------|------|-------|----------|---------------|-----|
| Qwen2-VL-2B | 2-4GB | ⚡⚡⚡ | ⭐⭐⭐ | High | 4-6GB |
| Qwen2-VL-7B | 8GB | ⚡⚡ | ⭐⭐⭐⭐ | Low | 8-12GB |
| LLaVA-1.5-7B | 7GB | ⚡⚡ | ⭐⭐⭐ | Medium | 8-10GB |

---

## Tuning Parameters

### Temperature
Controls randomness in output:
```bash
TEMPERATURE=0.1   # More deterministic (recommended for OCR)
TEMPERATURE=0.7   # More creative (not recommended)
```

### Max Tokens
Maximum length of response:
```bash
MAX_TOKENS=2000   # Standard (recommended)
MAX_TOKENS=4000   # For very detailed invoices
```

---

## Troubleshooting

### Model is hallucinating (making up data)

**Solutions:**
1. ✅ Use larger model (7B instead of 2B)
2. ✅ Lower temperature to 0.1
3. ✅ Improve prompt (already done in config.py)
4. ✅ Ensure image quality is good

### Model is too slow

**Solutions:**
1. Use smaller model (2B instead of 7B)
2. Reduce MAX_TOKENS
3. Close other applications

### Out of memory errors

**Solutions:**
1. Use smaller model (2B)
2. Close other applications
3. Restart your Mac

### Model not reading text correctly

**Solutions:**
1. Use 7B model (better OCR)
2. Ensure image is clear and high resolution
3. Try preprocessing image (increase contrast)

---

## Testing Different Models

Quick test script:
```bash
# Test current model
curl -X POST http://localhost:8000/extract \
  -F "image=@testdata/sample_receipt.png" | jq

# Check which model is loaded
curl http://localhost:8000/health | jq
```

---

## Recommended Settings

### For Development (Fast iteration)
```bash
MODEL_NAME=qwen/Qwen2-VL-2B-Instruct
MAX_TOKENS=2000
TEMPERATURE=0.1
```

### For Production (Best accuracy)
```bash
MODEL_NAME=qwen/Qwen2-VL-7B-Instruct
MAX_TOKENS=2000
TEMPERATURE=0.1
PRELOAD_MODEL=true  # Faster first request
```

### For Low Memory Systems
```bash
MODEL_NAME=qwen/Qwen2-VL-2B-Instruct
MAX_TOKENS=1500
TEMPERATURE=0.1
```

---

## Custom Models

You can use any MLX-compatible vision model from Hugging Face:

1. Find model on https://huggingface.co/models
2. Check if it's MLX-compatible
3. Update `.env`:
   ```bash
   MODEL_NAME=username/model-name
   ```
4. Restart service

**Note:** First run will download the model (~5-15 minutes depending on size).

---

## Current Issue: Hallucination

The 2B model tends to generate fake data instead of reading the actual receipt. This is because:
- Small models have limited OCR capabilities
- They try to "complete" the task even without reading properly

**Solution:** Use the 7B model which has better vision understanding and OCR capabilities.
