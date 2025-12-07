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

# Image Resizing (to prevent memory issues with large images)
# Max dimension (width or height) for resizing - lower = faster but less detail
MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", 1024))  # Default 1024px

# System Prompt for Receipt Extraction
# SYSTEM_PROMPT = """You are an expert receipt and invoice data extraction assistant. 
# Extract the following information from the receipt image and return ONLY a valid JSON object with no additional text:

# {
#   "vendor_name": "...",
#   "invoice_number": "...",
#   "invoice_date": "YYYY-MM-DD",
#   "due_date": "YYYY-MM-DD",
#   "items": [
#     {
#       "description": "...",
#       "details": ["...", "..."],
#       "quantity": 0.0,
#       "unit_price": 0.0,
#       "total": 0.0,
#       "currency": "...",
#       "category": "..."
#     }
#   ],
#   "subtotal": 0.0,
#   "tax_rate_percent": 0.0,
#   "tax_amount": 0.0,
#   "discount": 0.0,
#   "total_due": 0.0
# }

# Rules:
# - Use null for missing values
# - Dates must be in YYYY-MM-DD format
# - All monetary values should be numbers (not strings)
# - Infer item categories when possible (e.g., "Food", "Office Supplies", "Travel")
# - If you cannot determine a value, use null
# - Return ONLY the JSON object, no markdown formatting or additional text"""

USER_PROMPT = """IMPORTANT: Read the ACTUAL text from this receipt/invoice image. Do NOT make up or generate fake data.

CURRENCY RULE:
- For ALL extracted monetary fields, the currency MUST be "IDR".
- Ignore the absence of "Rp" or "IDR" in the image.
- Do NOT guess other currencies. Always output "IDR".

DATE FORMAT RULE (CRITICAL):
- ALL dates MUST be converted to YYYY-MM-DD format (e.g., "2015-12-05")
- If the receipt shows "05 Desember 2015", convert it to "2015-12-05"
- If the receipt shows "5/12/2015" or "05/12/2015", convert it to "2015-12-05"
- If the receipt shows "Dec 5, 2015", convert it to "2015-12-05"
- NEVER output dates in any other format. ALWAYS use YYYY-MM-DD.
- Month names in any language (January, Januari, Desember, etc.) must be converted to numbers.

Extract the following information from what you SEE in the image:
- vendor_name (company name at the top)
- invoice_number (invoice ID/number. If not present, use null)
- invoice_date (MUST be in YYYY-MM-DD format, e.g., "2015-12-05")
- due_date (MUST be in YYYY-MM-DD format, or null if not present)
- items (array of objects, EACH item MUST have ALL these fields):
  - description (string)
  - quantity (number)
  - unit_price (number)
  - total (number)
  - currency (string, ALWAYS "IDR")
  - category (string, MUST be one of: FOOD, GROCERIES, TRANSPORT, SHOPPING, ENTERTAINMENT, UTILITIES, SUBSCRIPTIONS, HEALTHCARE, OTHER)
- subtotal (subtotal amount)
- tax_rate_percent (tax percentage, e.g., 18.0 for 18%. If there is NO tax indication on the receipt, set tax_rate_percent to 0)
- tax_amount (tax amount in currency. If there is NO tax indication on the receipt, set tax_amount to 0)
- discount (discount amount, or 0 if none)
- total_due (final total amount)

EXAMPLE item format (EVERY item must follow this exact structure):
{"description": "Coffee", "quantity": 2, "unit_price": 15000, "total": 30000, "currency": "IDR", "category": "FOOD"}

Rules:
- Only extract data that is VISIBLE in the image
- DATES MUST BE IN YYYY-MM-DD FORMAT - convert from any format you see on the receipt
- If the receipt does NOT explicitly show tax, VAT, PPN, service charge, or similar, ALWAYS output tax_rate_percent = 0 and tax_amount = 0
- Use null for any field not present in the image (except tax and discount rules above)
- Do NOT invent or hallucinate data
- Return ONLY valid JSON, no markdown or extra text"""
