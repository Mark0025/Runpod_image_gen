# RunPod Image Server 🎨

A FastAPI server for viewing and managing AI-generated images from RunPod.

## Features

- 🖼️ **Image Gallery**: View all generated images in a beautiful grid layout
- 📤 **Upload Images**: Upload new images through the web interface
- 💾 **Save RunPod Images**: Automatically save images from RunPod API responses
- 🗑️ **Delete Images**: Remove unwanted images
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Setup

### 1. Virtual Environment

```bash
# Activate the virtual environment
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Dependencies are already installed via uv
# If you need to reinstall:
uv sync
```

### 3. Save Your RunPod Image

```bash
# Save the image we generated earlier
python save_runpod_image.py
```

### 4. Start the Server

```bash
# Start the FastAPI server
python main.py
```

### 5. Open in Browser

Navigate to: http://localhost:8001

## Usage

### Web Interface

- **Home Page**: View all images in a gallery format
- **Upload**: Drag & drop or select images to upload
- **View**: Click on images to see them full-size
- **Delete**: Remove images you no longer need

### API Endpoints

- `GET /` - Main gallery page
- `GET /api/images` - List all images (JSON)
- `GET /images/{filename}` - Serve an image file
- `POST /upload` - Upload a new image
- `POST /save-runpod-image` - Save RunPod generated image
- `DELETE /images/{filename}` - Delete an image

### Scripts

- **`scripts/runpod_api.sh`** - Submit image generation jobs to RunPod
- **`scripts/check_status.sh`** - Check job status and retrieve results
- **`save_runpod_image.py`** - Save RunPod images from base64 data

## Example Workflow

1. **Generate Image**:

   ```bash
   ./scripts/runpod_api.sh
   ```

2. **Check Status**:

   ```bash
   ./scripts/check_status.sh <job_id>
   ```

3. **Save Image** (when complete):

   ```bash
   python save_runpod_image.py
   ```

4. **View in Gallery**:
   - Start server: `python main.py`
   - Open: http://localhost:8001

## File Structure

```
.
├── main.py                 # FastAPI server
├── save_runpod_image.py   # Script to save RunPod images
├── scripts/               # RunPod API scripts
│   ├── runpod_api.sh     # Submit generation jobs
│   └── check_status.sh   # Check job status
├── generated_images/      # Directory for saved images
├── .env                   # Environment variables (API keys)
└── README.md             # This file
```

## Environment Variables

Create a `.env` file with your RunPod API key:

```bash
RUNPOD_API_KEY=your_api_key_here
```

## Troubleshooting

- **Port already in use**: Change the port in `main.py` or kill the process using port 8001
- **Permission denied**: Make sure scripts are executable: `chmod +x scripts/*.sh`
- **Images not showing**: Check that the `generated_images/` directory exists and contains image files

## Next Steps

- Add image editing capabilities
- Implement image tagging and search
- Add user authentication
- Create image sharing features
- Add batch processing for multiple images
