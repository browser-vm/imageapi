import io
import base64
import modal
from fastapi import HTTPException, Response
from pydantic import BaseModel

# 1. Define the environment and dependencies
app = modal.App("image-to-webp-optimizer")

# Create a container image with the required libraries
image = (
    modal.Image.debian_slim()
    .pip_install("requests", "Pillow", "fastapi", "pydantic")
)

# 2. Define the request schema
class ImageRequest(BaseModel):
    url: str

# 3. Create the webhook endpoint
# We allocate 8192MB of memory and a 5-minute timeout to safely handle 500MB files
@app.function(image=image, memory=8192, timeout=300)
@modal.web_endpoint(method="POST")
def optimize_image(req: ImageRequest):
    import requests
    from PIL import Image
    
    # Disable the max image pixels limit to allow processing of massive 500MB images
    Image.MAX_IMAGE_PIXELS = None
    MAX_SIZE_BYTES = 500 * 1024 * 1024 # 500MB

    # Step 1: Download the image
    try:
        response = requests.get(req.url, stream=True)
        response.raise_for_status()
        
        # Check headers first if available to save bandwidth
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Image exceeds the 500MB limit.")

        image_bytes = response.content
        
        # Double-check the actual downloaded size
        if len(image_bytes) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Image exceeds the 500MB limit.")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

    # Step 2: Process and optimize the image
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGBA if the image has a palette to preserve transparency in WebP
        if img.mode == "P" and "transparency" in img.info:
            img = img.convert("RGBA")
        elif img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        output_buffer = io.BytesIO()
        
        # Save as WEBP. Using lossless=True maintains the exact visual quality and dimensions.
        img.save(output_buffer, format="WEBP", lossless=True)
        optimized_bytes = output_buffer.getvalue()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

    # Step 3: Base64 encode and return raw string
    try:
        b64_encoded = base64.b64encode(optimized_bytes).decode('utf-8')
        # Return as raw text rather than JSON to avoid escaping characters
        return Response(content=b64_encoded, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode image: {str(e)}")