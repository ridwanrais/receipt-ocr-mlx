# Model Cache Cleanup Guide

## Overview

MLX-VLM models are cached locally in your Hugging Face cache directory. Each model can be several gigabytes, so it's important to clean up old models you're no longer using.

---

## Cache Location

Models are stored in:
```
~/.cache/huggingface/hub/
```

---

## Check Current Cache Usage

### View all cached models
```bash
du -sh ~/.cache/huggingface/hub/models--* | sort -hr
```

### Check specific model size
```bash
du -sh ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct
du -sh ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-7B-Instruct
```

### Total cache size
```bash
du -sh ~/.cache/huggingface/
```

---

## Clean Up Old Models

### Remove specific model
```bash
# Remove 2B model (saves ~4.1 GB)
rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct

# Remove 7B model (saves ~7 GB)
rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-7B-Instruct

# Remove LLaVA model
rm -rf ~/.cache/huggingface/hub/models--llava-hf--llava-1.5-7b-hf
```

### Remove all cached models (⚠️ Use with caution)
```bash
# This will delete ALL cached models
rm -rf ~/.cache/huggingface/hub/models--*
```

### Clean entire Hugging Face cache (⚠️ Use with extreme caution)
```bash
# This will delete everything including tokenizers, datasets, etc.
rm -rf ~/.cache/huggingface/
```

---

## Model Sizes

| Model | Approximate Size |
|-------|-----------------|
| Qwen2-VL-2B-Instruct | ~4.1 GB |
| Qwen2-VL-7B-Instruct | ~7.0 GB |
| LLaVA-1.5-7B | ~7.0 GB |

---

## Best Practices

### 1. Keep Only Active Model
If you're using the 7B model, remove the 2B:
```bash
rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct
```

### 2. Clean Before Switching
Before downloading a new model, remove the old one:
```bash
# Check what you have
ls ~/.cache/huggingface/hub/ | grep models--

# Remove old model
rm -rf ~/.cache/huggingface/hub/models--<old-model-name>

# Update .env to new model
# Restart service (new model will download)
```

### 3. Regular Cleanup
Check cache size monthly:
```bash
du -sh ~/.cache/huggingface/
```

---

## Troubleshooting

### Model won't delete (permission denied)
```bash
# Use sudo (be careful!)
sudo rm -rf ~/.cache/huggingface/hub/models--<model-name>
```

### Model re-downloads after deletion
This is normal. The service will re-download the model specified in `.env` when you make a request.

### How to prevent auto-download
Stop the service before cleaning:
```bash
# Stop service
lsof -ti:8000 | xargs kill -9

# Clean cache
rm -rf ~/.cache/huggingface/hub/models--*

# Update .env to desired model
# Start service (will download only the specified model)
make run
```

---

## Space Saved Examples

### Scenario 1: Switch from 2B to 7B
```bash
# Before: 2B model (4.1 GB)
# After: 7B model (7.0 GB)
# Net change: +2.9 GB

# Clean up 2B to save space:
rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct
# Final: 7.0 GB (saved 4.1 GB from having both)
```

### Scenario 2: Multiple models tested
```bash
# If you tested multiple models:
# - 2B: 4.1 GB
# - 7B: 7.0 GB  
# - LLaVA: 7.0 GB
# Total: ~18 GB

# Keep only 7B:
rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct
rm -rf ~/.cache/huggingface/hub/models--llava-hf--llava-1.5-7b-hf
# Final: 7.0 GB (saved 11 GB)
```

---

## Automated Cleanup Script

Create a cleanup script:

```bash
#!/bin/bash
# cleanup_models.sh

echo "Current cache usage:"
du -sh ~/.cache/huggingface/hub/

echo -e "\nCached models:"
ls -lh ~/.cache/huggingface/hub/ | grep models--

echo -e "\nDo you want to remove unused models? (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo "Which model to keep?"
    echo "1) Qwen2-VL-2B-Instruct"
    echo "2) Qwen2-VL-7B-Instruct"
    echo "3) Keep all"
    read -r choice
    
    case $choice in
        1)
            rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-7B-Instruct
            echo "Removed 7B model"
            ;;
        2)
            rm -rf ~/.cache/huggingface/hub/models--qwen--Qwen2-VL-2B-Instruct
            echo "Removed 2B model"
            ;;
        3)
            echo "No models removed"
            ;;
    esac
fi

echo -e "\nFinal cache usage:"
du -sh ~/.cache/huggingface/hub/
```

Make it executable:
```bash
chmod +x cleanup_models.sh
./cleanup_models.sh
```

---

## Quick Reference

```bash
# Check cache size
du -sh ~/.cache/huggingface/hub/

# List all models
ls ~/.cache/huggingface/hub/ | grep models--

# Remove specific model
rm -rf ~/.cache/huggingface/hub/models--<model-name>

# Check space saved
df -h ~
```

---

## Recent Cleanup

**Date:** November 23, 2025

**Action:** Removed Qwen2-VL-2B-Instruct

**Result:**
- Space freed: 4.1 GB
- Current model: Qwen2-VL-7B-Instruct (7.0 GB)
- Total cache: 7.0 GB (down from 11.1 GB)

---

## When to Clean Up

✅ **Clean up when:**
- Switching to a different model permanently
- Running low on disk space
- You've tested multiple models and decided on one
- Monthly maintenance

❌ **Don't clean up when:**
- You frequently switch between models
- You're still testing different models
- You have plenty of disk space
- Model is currently in use by the service

---

## Notes

- Models will re-download automatically when needed
- First download takes 5-15 minutes depending on model size
- Subsequent requests use cached model (fast)
- Cache is shared across all Python projects using Hugging Face
