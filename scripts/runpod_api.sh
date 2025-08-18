#!/bin/bash

# Source the .env file to get the API key
source .env

# Check if API key is loaded
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "Error: RUNPOD_API_KEY not found in .env file"
    exit 1
fi

# RunPod API endpoint ID
ENDPOINT_ID="aj1jw0guu5uziz"

# Run the API request
curl -X POST "https://api.runpod.ai/v2/$ENDPOINT_ID/run" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $RUNPOD_API_KEY" \
    -d '{"input": {"prompt": "A cute fluffy white dog in the style of a Pixar animation 3D drawing."}}'

echo ""
echo "API request completed!"
