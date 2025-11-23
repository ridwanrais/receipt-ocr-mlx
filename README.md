# Receipt OCR MLX

A high-performance receipt OCR and data extraction service using MLX-VLM (Apple Silicon optimized vision-language models).

## Features

- 🚀 Fast inference on Apple Silicon (M1/M2/M3)
- 🎯 Specialized for receipt/invoice data extraction
- 🔒 Runs locally - no API costs or data privacy concerns
- 📊 Structured JSON output
- 🔄 RESTful API for easy integration

## Requirements

- Apple Silicon Mac (M1/M2/M3)
- Python 3.9+
- 8GB+ RAM recommended

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Start the service

```bash
python app.py
```

The service will start on `http://localhost:8000`

### API Endpoints

#### POST /extract
Extract receipt data from an image

**Request:**
```bash
curl -X POST http://localhost:8000/extract -F "image=@testdata/sample_receipt.png"         
```

**Response:**
```json
{
  "vendor_name": "J.Co",
  "invoice_number": "12345",
  "invoice_date": "2024-01-15",
  "due_date": "2024-01-15",
  "items": [
    {
      "description": "Caffe Latte",
      "details": ["Grande", "Whole Milk"],
      "quantity": 1.0,
      "unit_price": 4.95,
      "total": 4.95,
      "category": "Food & Beverage"
    }
  ],
  "subtotal": 4.95,
  "tax_rate_percent": 10.0,
  "tax_amount": 0.50,
  "discount": 0.0,
  "total_due": 5.45
}
```

#### GET /health
Health check endpoint

## Configuration

Edit `config.py` to customize:
- Model selection
- Port number
- Max image size
- Timeout settings

## Integration with Go Backend

Update your Go backend's `.env`:

```bash
# Use local MLX service instead of OpenRouter
USE_MLX_SERVICE=true
MLX_SERVICE_URL=http://localhost:8000
```

## Models

Default model: `qwen/Qwen2-VL-2B-Instruct`

Other supported models:
- `qwen/Qwen2-VL-7B-Instruct` (better accuracy, slower)
- `llava-hf/llava-1.5-7b-hf` (general purpose)

Change model in `config.py`

## Performance

Typical inference times on M2 Pro:
- First request: ~5-10s (model loading)
- Subsequent requests: ~2-4s

## Troubleshooting

### Model download fails
```bash
# Manually download model
python -c "from mlx_vlm import load; load('qwen/Qwen2-VL-2B-Instruct')"
```

### Out of memory
- Use smaller model (2B instead of 7B)
- Close other applications
- Reduce max_tokens in config

## License

MIT
