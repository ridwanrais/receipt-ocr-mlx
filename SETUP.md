# Receipt OCR MLX - Setup Instructions

## Prerequisites

✅ **Required:**
- Apple Silicon Mac (M1/M2/M3)
- Python 3.9 or higher
- 8GB+ RAM available

✅ **Check your system:**
```bash
# Check if you have Apple Silicon
uname -m
# Should output: arm64

# Check Python version
python3 --version
# Should be 3.9 or higher
```

## Installation Steps

### Step 1: Navigate to Project

```bash
cd /Users/ridwanrais/Code/personal/invoice-management/receipt-ocr-mlx
```

### Step 2: Install Dependencies

```bash
make install
```

This will:
- Create a Python virtual environment
- Install all required packages (including mlx-vlm)
- Create `.env` file from template

**Expected time:** 2-5 minutes (depending on internet speed)

### Step 3: (Optional) Customize Configuration

Edit `.env` file if needed:

```bash
# Default settings work fine for most cases
# Only edit if you want to:
# - Change port (default: 8000)
# - Use different model
# - Adjust timeouts
```

### Step 4: Start the Service

```bash
make run
```

**First startup will:**
- Download the model (~2-4GB)
- Load model into memory
- Start Flask server

**Expected time for first run:** 5-10 minutes (model download)

**Subsequent runs:** 10-30 seconds (model loading only)

You should see:
```
INFO:__main__:Starting MLX-VLM Receipt Scanner Service on 0.0.0.0:8000
INFO:__main__:Model: qwen/Qwen2-VL-2B-Instruct
 * Running on http://0.0.0.0:8000
```

### Step 5: Test the Service

In a new terminal:

```bash
cd /Users/ridwanrais/Code/personal/invoice-management/receipt-ocr-mlx

# Activate virtual environment
source venv/bin/activate

# Test health endpoint
python test_service.py

# Test with a receipt image (if you have one)
python test_service.py path/to/receipt.jpg
```

## Quick Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Test extraction (replace with your image path)
curl -X POST http://localhost:8000/extract \
  -F "image=@/path/to/receipt.jpg"
```

## Common Issues & Solutions

### Issue: "command not found: make"

**Solution:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### Issue: "python3: command not found"

**Solution:**
```bash
# Install Python via Homebrew
brew install python@3.11
```

### Issue: "pip install fails"

**Solution:**
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Try installing again
cd receipt-scanner-mlx-service
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Model download is slow/stuck

**Solution:**
- Check internet connection
- Download may take 5-10 minutes for 2-4GB model
- If stuck, cancel (Ctrl+C) and restart

### Issue: "Out of memory" error

**Solutions:**
1. Close other applications
2. Use smaller model:
   ```bash
   # Edit .env
   MODEL_NAME=qwen/Qwen2-VL-2B-Instruct  # Smaller, faster
   ```
3. Restart your Mac to free up memory

### Issue: Service starts but crashes on first request

**Solution:**
- Model might not be fully loaded
- Check logs for specific error
- Try preloading model:
  ```bash
  # Edit .env
  PRELOAD_MODEL=true
  ```

## Verifying Installation

✅ **Service is working if:**

1. Health check returns 200:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","model":"qwen/Qwen2-VL-2B-Instruct","model_loaded":true}
   ```

2. Extract endpoint accepts images:
   ```bash
   curl -X POST http://localhost:8000/extract -F "image=@receipt.jpg"
   # Should return JSON with receipt data
   ```

## Next Steps

Once the service is running:

1. **Test with your receipts** - Try different receipt images
2. **Integrate with Go backend** - Follow `INTEGRATION.md`
3. **Optimize performance** - Adjust settings in `.env`

## Stopping the Service

Press `Ctrl+C` in the terminal where the service is running.

## Uninstalling

```bash
cd /Users/ridwanrais/Code/personal/invoice-management/receipt-ocr-mlx
make clean
rm -rf venv .env
```

## Getting Help

If you encounter issues:

1. Check logs in the terminal
2. Review `README.md` for detailed documentation
3. Check `INTEGRATION.md` for Go backend integration
4. Review MLX-VLM documentation: https://github.com/Blaizzy/mlx-vlm

## Performance Expectations

| Hardware | Model Size | First Load | Inference Time |
|----------|-----------|------------|----------------|
| M1 8GB | 2B | 5-10s | 2-4s |
| M1 16GB | 2B | 5-10s | 2-3s |
| M2 Pro | 2B | 3-5s | 1-2s |
| M2 Pro | 7B | 10-15s | 4-6s |
| M3 Max | 7B | 5-10s | 2-4s |

## Resource Usage

- **Disk Space:** ~4-8GB (model + dependencies)
- **RAM:** ~4-8GB during inference
- **CPU:** Minimal (MLX uses Neural Engine)

---

**Ready to start?** Run `make install` then `make run`! 🚀
