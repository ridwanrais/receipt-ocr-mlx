# Integration Guide: MLX Service with Go Backend

This guide explains how to integrate the MLX-VLM service with your existing Go backend.

## Quick Start

### 1. Setup MLX Service

```bash
cd receipt-ocr-mlx

# Install dependencies
make install

# Start the service
make run
```

The service will start on `http://localhost:8000`

### 2. Update Go Backend

Add to your `.env` file in `receipt-scanner-be`:

```bash
# MLX Service Configuration
USE_MLX_SERVICE=true
MLX_SERVICE_URL=http://localhost:8000
MLX_TIMEOUT=300
```

### 3. Update Service Layer

The Go backend needs to be modified to use MLX client when `USE_MLX_SERVICE=true`.

Edit `receipt-scanner-be/internal/service/receipt_service.go`:

```go
import (
    "github.com/ridwanfathin/invoice-processor-service/internal/mlxclient"
    // ... other imports
)

type receiptService struct {
    // ... existing fields
    mlxClient     *mlxclient.Client
    useMLXService bool
}

func NewReceiptService(repo repository.ReceiptRepository, openRouterClient *openrouter.Client, mlxClient *mlxclient.Client, useMLXService bool, maxWorkers int) ReceiptService {
    return &receiptService{
        // ... existing fields
        mlxClient:     mlxClient,
        useMLXService: useMLXService,
    }
}

// In ScanReceipt method, add logic to choose client:
func (s *receiptService) ScanReceipt(ctx context.Context, imageData []byte) (*domain.Receipt, error) {
    var invoice *domain.Invoice
    var err error
    
    if s.useMLXService && s.mlxClient != nil {
        // Use local MLX service
        invoice, err = s.mlxClient.ExtractInvoiceData(imageData)
    } else {
        // Use OpenRouter
        invoice, err = s.openRouterClient.ExtractInvoiceData(imageData)
    }
    
    if err != nil {
        return nil, fmt.Errorf("extract_receipt_data: %w", err)
    }
    
    // ... rest of the method
}
```

### 4. Update Main.go

Edit `receipt-scanner-be/cmd/server/main.go`:

```go
// After loading config...

var mlxClient *mlxclient.Client
if cfg.UseMLXService {
    log.Println("Initializing MLX-VLM client...")
    mlxClient = mlxclient.NewClient(&mlxclient.Config{
        BaseURL: cfg.MLXServiceURL,
        Timeout: cfg.MLXTimeout,
    })
    
    // Health check
    if err := mlxClient.HealthCheck(); err != nil {
        log.Printf("Warning: MLX service health check failed: %v", err)
        log.Println("Falling back to OpenRouter...")
        cfg.UseMLXService = false
    } else {
        log.Println("MLX service is healthy")
    }
}

// Update service initialization
receiptService := service.NewReceiptService(
    receiptRepo, 
    openRouterClient, 
    mlxClient,
    cfg.UseMLXService,
    cfg.MaxWorkers,
)
```

## Testing

### Test MLX Service Standalone

```bash
cd receipt-ocr-mlx

# Test with a receipt image
python test_service.py path/to/receipt.jpg
```

### Test Full Integration

1. Start MLX service:
```bash
cd receipt-ocr-mlx
make run
```

2. In another terminal, start Go backend:
```bash
cd receipt-scanner-be
make hotreload
```

3. Test the endpoint:
```bash
curl -X POST http://localhost:8080/v1/receipts/scan \
  -F "receiptImage=@receipt.jpg"
```

## Performance Comparison

| Method | First Request | Subsequent | Cost |
|--------|--------------|------------|------|
| OpenRouter (Grok) | 60s+ | 60s+ | Free (rate limited) |
| OpenRouter (Gemini) | 5-15s | 5-15s | Free (rate limited) |
| MLX Local (2B) | 5-10s | 2-4s | Free (unlimited) |
| MLX Local (7B) | 10-20s | 5-8s | Free (unlimited) |

## Troubleshooting

### MLX Service Won't Start

**Error: "No module named 'mlx_vlm'"**
```bash
cd receipt-scanner-mlx-service
source venv/bin/activate
pip install mlx-vlm
```

**Error: "Model download failed"**
- Check internet connection
- Manually download: `python -c "from mlx_vlm import load; load('qwen/Qwen2-VL-2B-Instruct')"`

### Go Backend Can't Connect

**Error: "connection refused"**
- Ensure MLX service is running: `curl http://localhost:8000/health`
- Check MLX service logs
- Verify `MLX_SERVICE_URL` in `.env`

### Slow Performance

- Use smaller model (2B instead of 7B)
- Close other applications
- Check Activity Monitor for memory pressure
- Consider preloading model: Set `PRELOAD_MODEL=true` in MLX service `.env`

## Fallback Strategy

The integration supports automatic fallback:

1. Try MLX service if `USE_MLX_SERVICE=true`
2. If MLX service fails health check, fall back to OpenRouter
3. Log warnings for debugging

## Production Considerations

### For Development
- Use MLX service locally (fast, free, unlimited)
- Keep OpenRouter as fallback

### For Production
- Deploy MLX service on Apple Silicon server
- Use load balancer for multiple MLX instances
- Keep OpenRouter as fallback for high load
- Monitor both services

## Environment Variables Summary

### MLX Service (.env)
```bash
HOST=0.0.0.0
PORT=8000
MODEL_NAME=qwen/Qwen2-VL-2B-Instruct
MAX_TOKENS=1000
TEMPERATURE=0.1
PRELOAD_MODEL=false
```

### Go Backend (.env)
```bash
USE_MLX_SERVICE=true
MLX_SERVICE_URL=http://localhost:8000
MLX_TIMEOUT=300

# Keep OpenRouter config as fallback
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL_ID=google/gemini-flash-1.5
OPENROUTER_TIMEOUT=300
```

## Next Steps

1. ✅ Setup MLX service
2. ✅ Test standalone
3. ⏳ Integrate with Go backend (requires code changes)
4. ⏳ Test full integration
5. ⏳ Deploy to production (optional)
