"""MLX-VLM Receipt Scanner Service"""
import json
import logging
import os
import tempfile
from io import BytesIO

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import mlx_vlm
import requests

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global model cache
model = None
processor = None


def load_model():
    """Load the MLX-VLM model (lazy loading)"""
    global model, processor
    
    if model is None:
        logger.info(f"Loading model: {config.MODEL_NAME}")
        try:
            model, processor = mlx_vlm.load(config.MODEL_NAME)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    return model, processor


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def extract_json_from_response(text):
    """Extract JSON from model response, handling markdown code blocks"""
    text = text.strip()
    
    # Try to extract JSON from markdown code blocks first
    import re
    json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_blocks:
        # Try each block until we find valid JSON
        for block in json_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON object without code blocks
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        json_str = text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Attempted to parse: {json_str[:500]}")
            raise
    
    raise ValueError("No valid JSON object found in response")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": config.MODEL_NAME,
        "model_loaded": model is not None
    })


@app.route('/extract', methods=['POST'])
def extract_receipt():
    """Extract receipt data from uploaded image or image URL"""
    try:
        image = None
        image_source = None
        
        # Check if image URL is provided (JSON request)
        if request.is_json:
            data = request.get_json()
            image_url = data.get('image_url')
            
            if not image_url:
                return jsonify({"error": "No image_url provided in JSON body"}), 400
            
            logger.info(f"Processing image from URL: {image_url}")
            image_source = image_url
            
            # Download image from URL
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    return jsonify({"error": f"URL does not point to an image. Content-Type: {content_type}"}), 400
                
                # Check file size
                file_size = len(response.content)
                if file_size > config.MAX_IMAGE_SIZE:
                    return jsonify({"error": f"Image too large. Max size: {config.MAX_IMAGE_SIZE} bytes"}), 400
                
                logger.info(f"Downloaded image ({file_size} bytes)")
                
                # Load image
                image = Image.open(BytesIO(response.content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download image from URL: {e}")
                return jsonify({"error": f"Failed to download image: {str(e)}"}), 400
            except Exception as e:
                logger.error(f"Failed to load image from URL: {e}")
                return jsonify({"error": "Invalid image from URL"}), 400
        
        # Check if image file is uploaded (multipart/form-data request)
        elif 'image' in request.files:
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": f"File type not allowed. Allowed types: {config.ALLOWED_EXTENSIONS}"}), 400
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > config.MAX_IMAGE_SIZE:
                return jsonify({"error": f"File too large. Max size: {config.MAX_IMAGE_SIZE} bytes"}), 400
            
            logger.info(f"Processing uploaded image: {file.filename} ({file_size} bytes)")
            image_source = file.filename
            
            # Load image
            try:
                image = Image.open(BytesIO(file.read()))
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return jsonify({"error": "Invalid image file"}), 400
        
        else:
            return jsonify({"error": "No image file or image_url provided"}), 400
        
        # At this point, we have a valid PIL Image object
        
        # Load model (lazy loading)
        try:
            model_obj, processor_obj = load_model()
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return jsonify({"error": "Model initialization failed"}), 500
        
        # Save image temporarily for mlx_vlm
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image.save(tmp_file.name)
            tmp_image_path = tmp_file.name
        
        try:
            # Verify image was saved
            logger.info(f"Temp image saved: {tmp_image_path}, exists: {os.path.exists(tmp_image_path)}, size: {os.path.getsize(tmp_image_path)} bytes")
            
            # Prepare messages in the format Qwen2-VL expects
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": tmp_image_path},
                        {"type": "text", "text": config.USER_PROMPT}
                    ]
                }
            ]
            
            logger.info(f"Generating response from model with max_tokens={config.MAX_TOKENS}...")
            logger.info(f"Image path: {tmp_image_path}")
            
            # Apply chat template to format the prompt correctly
            # Get model config
            model_config = model_obj.config if hasattr(model_obj, 'config') else {}
            
            prompt = mlx_vlm.apply_chat_template(
                processor_obj,
                model_config,
                messages,
                num_images=1
            )
            
            logger.info(f"Formatted prompt type: {type(prompt)}")
            
            result = mlx_vlm.generate(
                model_obj,
                processor_obj,
                prompt,
                image=tmp_image_path,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                verbose=True
            )
            
            # Extract text from GenerationResult
            response = result.text if hasattr(result, 'text') else str(result)
            logger.info(f"Model generated {result.generation_tokens} tokens in {result.generation_tps:.1f} tokens/sec")
            
            # Extract JSON from response
            receipt_data = extract_json_from_response(response)
            
            logger.info("Successfully extracted receipt data")
            return jsonify(receipt_data), 200
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from model response: {e}")
            return jsonify({
                "error": "Failed to parse model response as JSON",
                "raw_response": response[:1000]  # Return first 1000 chars for debugging
            }), 500
        except ValueError as e:
            logger.error(f"No valid JSON in response: {e}")
            return jsonify({
                "error": f"Model inference failed: {str(e)}",
                "raw_response": response[:1000] if 'response' in locals() else "No response"
            }), 500
        except Exception as e:
            logger.error(f"Model inference failed: {e}")
            return jsonify({
                "error": f"Model inference failed: {str(e)}",
                "raw_response": response[:1000] if 'response' in locals() else "No response"
            }), 500
        finally:
            # Clean up temp file
            if os.path.exists(tmp_image_path):
                os.unlink(tmp_image_path)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        "current_model": config.MODEL_NAME,
        "recommended_models": [
            "qwen/Qwen2-VL-2B-Instruct",
            "qwen/Qwen2-VL-7B-Instruct",
            "llava-hf/llava-1.5-7b-hf"
        ]
    })


if __name__ == '__main__':
    logger.info(f"Starting MLX-VLM Receipt Scanner Service on {config.HOST}:{config.PORT}")
    logger.info(f"Model: {config.MODEL_NAME}")
    
    # Optionally preload model at startup
    if os.getenv("PRELOAD_MODEL", "false").lower() == "true":
        logger.info("Preloading model...")
        load_model()
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
