from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse

import os
import base64
import json
import time
import requests
from datetime import datetime
import aiofiles
from pathlib import Path

app = FastAPI(title="RunPod Image Server", description="Server for viewing and managing RunPod generated images")

# Create directories if they don't exist
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

def fix_base64_padding(data: str) -> str:
    """Fix base64 padding by adding = characters as needed"""
    padding_needed = (4 - len(data) % 4) % 4
    return data + ('=' * padding_needed)

# No static files needed for this simple image server

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page with image gallery"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RunPod Image Gallery</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { text-align: center; margin-bottom: 30px; }
            .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
            .image-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .image-card img { width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }
            .image-info { margin-top: 10px; font-size: 14px; color: #666; }
            .upload-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .upload-form { display: flex; gap: 10px; align-items: center; }
            input[type="file"] { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            
            .generate-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .generate-form { display: flex; flex-direction: column; gap: 15px; }
            .form-group { display: flex; flex-direction: column; gap: 5px; }
            .form-group label { font-weight: bold; color: #333; }
            .form-group textarea { padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; resize: vertical; }
            .form-group textarea:focus { outline: none; border-color: #007bff; box-shadow: 0 0 0 2px rgba(0,123,255,0.25); }
            
            .progress-bar { width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; margin-top: 10px; }
            .progress-fill { height: 100%; background: linear-gradient(90deg, #007bff, #28a745); animation: progress-animation 2s ease-in-out infinite; }
            @keyframes progress-animation { 0% { width: 0%; } 50% { width: 70%; } 100% { width: 100%; } }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎨 RunPod Image Gallery</h1>
            <p>View and manage your AI-generated images</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                🔄 Reload Page
            </button>
        </div>
        
        <div class="upload-section">
            <h3>Upload New Image</h3>
            <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required>
                <button type="submit">Upload</button>
            </form>
        </div>
        
        <div class="generate-section">
            <h3>🎨 Generate New AI Image</h3>
            <form class="generate-form" id="generateForm">
                <div class="form-group">
                    <label for="prompt">Describe your image:</label>
                    <textarea id="prompt" name="prompt" rows="3" placeholder="A cute fluffy white dog in the style of a Pixar animation 3D drawing..." required></textarea>
                </div>
                <button type="submit" id="generateBtn">🚀 Generate Image</button>
            </form>
            <div id="generateStatus" style="display: none;">
                <p>⏳ Generating image... This may take a few minutes.</p>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        </div>
        
        <div class="gallery" id="imageGallery">
            <!-- Images will be loaded here -->
        </div>
        
        <script>
            // Load images on page load
            window.onload = function() {
                loadImages();
            };
            
            async function loadImages() {
                try {
                    const response = await fetch('/api/images');
                    const images = await response.json();
                    const gallery = document.getElementById('imageGallery');
                    
                    if (images.length === 0) {
                        gallery.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: #666;">No images found. Upload some images to get started!</p>';
                        return;
                    }
                    
                    gallery.innerHTML = images.map(img => `
                        <div class="image-card">
                            <img src="/images/${img.filename}?v=${Date.now()}" alt="${img.filename}" 
                                 onload="console.log('✅ Image loaded:', img.filename)" 
                                 onerror="console.error('❌ Image failed to load:', img.filename, this.src, this.naturalWidth, this.naturalHeight)">
                            <div class="image-info">
                                <strong>${img.filename}</strong><br>
                                Uploaded: ${new Date(img.upload_time * 1000).toLocaleString()}<br>
                                Size: ${(img.size / 1024).toFixed(1)} KB<br>
                                <small style="color: #999;">URL: /images/${img.filename}</small>
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading images:', error);
                }
            }
            
            // Handle image generation form
            document.getElementById('generateForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const prompt = document.getElementById('prompt').value;
                const generateBtn = document.getElementById('generateBtn');
                const generateStatus = document.getElementById('generateStatus');
                
                if (!prompt.trim()) {
                    alert('Please enter a description for your image');
                    return;
                }
                
                // Show status and disable button
                generateBtn.disabled = true;
                generateBtn.textContent = '⏳ Generating...';
                generateStatus.style.display = 'block';
                
                try {
                    // Send generation request
                    const response = await fetch('/api/generate-image', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('🎉 Image generated successfully! Check the gallery below.');
                        // Reload images to show the new one
                        loadImages();
                    } else {
                        alert('❌ Error generating image: ' + result.message);
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('❌ Error generating image. Please try again.');
                } finally {
                    // Reset form and button
                    generateBtn.disabled = false;
                    generateBtn.textContent = '🚀 Generate Image';
                    generateStatus.style.display = 'none';
                    document.getElementById('prompt').value = '';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/images")
async def get_images():
    """Get list of all generated images"""
    images = []
    for file_path in IMAGES_DIR.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            stat = file_path.stat()
            images.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "upload_time": stat.st_mtime
            })
    
    # Sort by upload time (newest first)
    images.sort(key=lambda x: x["upload_time"], reverse=True)
    return images

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve an image file"""
    file_path = IMAGES_DIR / filename
    if not file_path.exists():
        print(f"❌ Image not found: {filename}")
        raise HTTPException(status_code=404, detail="Image not found")
    
    print(f"🖼️ Serving image: {filename} (size: {file_path.stat().st_size} bytes)")
    return FileResponse(file_path)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a new image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"uploaded_{timestamp}.{extension}"
    
    file_path = IMAGES_DIR / filename
    
    # Save the file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {"message": "Image uploaded successfully", "filename": filename}

@app.post("/save-runpod-image")
async def save_runpod_image(image_data: dict):
    """Save a RunPod generated image from base64 data"""
    try:
        # Extract image data from RunPod response
        if "output" in image_data and "images" in image_data["output"]:
            image_base64 = image_data["output"]["images"][0]
        else:
            raise HTTPException(status_code=400, detail="Invalid image data format")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"runpod_{timestamp}.png"
        file_path = IMAGES_DIR / filename
        
        # Decode and save base64 image with padding fix
        # Strip data URI prefix if present
        if image_base64.startswith('data:image/'):
            print(f"🔧 Stripping data URI prefix from {len(image_base64)} chars")
            image_base64 = image_base64.split(',', 1)[1]
        
        fixed_data = fix_base64_padding(image_base64)
        print(f"🔧 Fixed padding: {len(image_base64)} -> {len(fixed_data)} chars")
        
        image_bytes = base64.b64decode(fixed_data)
        print(f"🔧 Decoded to {len(image_bytes)} bytes")
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_bytes)
        
        return {"message": "Image saved successfully", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

@app.post("/api/generate-image")
async def generate_image(request: dict):
    """Generate an image using RunPod API"""
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Load API key from .env
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("RUNPOD_API_KEY")
        endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID", "aj1jw0guu5uziz")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="RunPod API key not configured")
        
        # Step 1: Submit generation request
        
        submit_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {
                "prompt": prompt
            }
        }
        
        print(f"🚀 Submitting generation request for prompt: {prompt}")
        response = requests.post(submit_url, headers=headers, json=payload)
        response.raise_for_status()
        
        job_data = response.json()
        job_id = job_data.get("id")
        
        if not job_id:
            raise HTTPException(status_code=500, detail="No job ID received from RunPod")
        
        print(f"📋 Job submitted with ID: {job_id}")
        
        # Step 2: Poll for completion
        status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
        max_attempts = 60  # 5 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"⏳ Checking status (attempt {attempt}/{max_attempts})...")
            
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            job_status = status_response.json()
            status = job_status.get("status")
            
            if status == "COMPLETED":
                print("✅ Job completed successfully!")
                
                # Step 3: Extract and save image
                if "output" in job_status:
                    output_item = job_status["output"]
                    
                    # Handle both image formats
                    image_data = None
                    if "images" in output_item and isinstance(output_item["images"], list) and len(output_item["images"]) > 0:
                        image_data = output_item["images"][0]
                    elif "image_url" in output_item:
                        image_data = output_item["image_url"]
                    
                    if image_data:
                        # Generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_prompt = safe_prompt.replace(' ', '_')
                        filename = f"generated_{safe_prompt}_{timestamp}.png"
                        file_path = IMAGES_DIR / filename
                        
                        # Decode and save base64 image with automatic padding fix
                        try:
                            # Strip data URI prefix if present
                            if image_data.startswith('data:image/'):
                                print(f"🔧 Stripping data URI prefix from {len(image_data)} chars")
                                image_data = image_data.split(',', 1)[1]
                            
                            # Fix padding and decode
                            fixed_data = fix_base64_padding(image_data)
                            print(f"🔧 Fixed padding: {len(image_data)} -> {len(fixed_data)} chars")
                            
                            image_bytes = base64.b64decode(fixed_data)
                            print(f"🔧 Decoded to {len(image_bytes)} bytes")
                            
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(image_bytes)
                        except Exception as decode_error:
                            print(f"❌ Base64 decode error: {decode_error}")
                            print(f"Image data length: {len(image_data)}")
                            print(f"Image data preview: {image_data[:100]}...")
                            raise HTTPException(status_code=500, detail=f"Error decoding image data: {str(decode_error)}")
                        
                        print(f"💾 Image saved as: {filename}")
                        
                        return {
                            "status": "success",
                            "message": "Image generated and saved successfully",
                            "filename": filename,
                            "prompt": prompt
                        }
                    else:
                        raise HTTPException(status_code=500, detail="No image data found in job output")
                else:
                    raise HTTPException(status_code=500, detail="No output data in completed job")
                    
            elif status == "FAILED":
                error_msg = job_status.get("error", "Unknown error")
                print(f"❌ Job failed: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Image generation failed: {error_msg}")
            
            # Wait before next check
            import asyncio
            await asyncio.sleep(5)
        
        # If we get here, job didn't complete in time
        raise HTTPException(status_code=408, detail="Image generation timed out after 5 minutes")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Error communicating with RunPod: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.delete("/images/{filename}")
async def delete_image(filename: str):
    """Delete an image"""
    file_path = IMAGES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        file_path.unlink()
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

@app.get("/share/{filename}")
async def share_image(filename: str):
    """Get shareable link and info for an image"""
    file_path = IMAGES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    stat = file_path.stat()
    share_info = {
        "filename": filename,
        "share_url": f"http://localhost:8001/images/{filename}",
        "direct_link": f"http://localhost:8001/images/{filename}",
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "upload_time": stat.st_mtime,
        "upload_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "content_type": "image/png" if filename.endswith('.png') else "image/jpeg"
    }
    
    return share_info

@app.post("/api/request")
async def process_request(request_data: dict):
    """General endpoint to process requests and return responses"""
    try:
        # Extract request details
        request_type = request_data.get("type", "general")
        message = request_data.get("message", "")
        data = request_data.get("data", {})
        
        # Process different request types
        if request_type == "image_info":
            # Return information about available images
            images = []
            for file_path in IMAGES_DIR.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    stat = file_path.stat()
                    images.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "upload_time": stat.st_mtime
                    })
            
            response = {
                "status": "success",
                "type": "image_info",
                "message": f"Found {len(images)} images",
                "data": {
                    "total_images": len(images),
                    "images": images
                }
            }
        
        elif request_type == "system_status":
            # Return system status
            import psutil
            response = {
                "status": "success",
                "type": "system_status",
                "message": "System status retrieved",
                "data": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "server_time": datetime.now().isoformat()
                }
            }
        
        elif request_type == "custom":
            # Handle custom requests
            response = {
                "status": "success",
                "type": "custom",
                "message": f"Processed custom request: {message}",
                "data": {
                    "received_data": data,
                    "processed_at": datetime.now().isoformat(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        
        else:
            # General response
            response = {
                "status": "success",
                "type": "general",
                "message": f"Request processed: {message}",
                "data": {
                    "received_data": data,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "type": "error",
            "message": f"Error processing request: {str(e)}",
            "data": {}
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "RunPod Image Server",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable for Docker compatibility
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
