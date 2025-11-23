"""Configuration for MLX-VLM Receipt Scanner Service"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/Qwen2-VL-2B-Instruct")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Image Processing
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 10 * 1024 * 1024))  # 10MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# System Prompt for Receipt Extraction
SYSTEM_PROMPT = """You are an expert receipt and invoice data extraction assistant. 
Extract the following information from the receipt image and return ONLY a valid JSON object with no additional text:

{
  "vendor_name": "...",
  "invoice_number": "...",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "items": [
    {
      "description": "...",
      "details": ["...", "..."],
      "quantity": 0.0,
      "unit_price": 0.0,
      "total": 0.0,
      "category": "..."
    }
  ],
  "subtotal": 0.0,
  "tax_rate_percent": 0.0,
  "tax_amount": 0.0,
  "discount": 0.0,
  "total_due": 0.0
}

Rules:
- Use null for missing values
- Dates must be in YYYY-MM-DD format
- All monetary values should be numbers (not strings)
- Infer item categories when possible (e.g., "Food", "Office Supplies", "Travel")
- If you cannot determine a value, use null
- Return ONLY the JSON object, no markdown formatting or additional text"""

USER_PROMPT = """Extract all information from this receipt image and return as JSON with these fields:
- vendor_name
- invoice_number
- invoice_date (YYYY-MM-DD)
- due_date (YYYY-MM-DD)
- items (array with description, quantity, unit_price, total, category)
- subtotal
- tax_rate_percent
- tax_amount
- discount
- total_due

Return only valid JSON, no other text."""
