#!/bin/bash

# Source the .env file to get the API key
source .env

# Check if API key is loaded
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "Error: RUNPOD_API_KEY not found in .env file"
    exit 1
fi

# Check if job ID is provided as argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <job_id>"
    echo "Example: $0 c2fa888b-7c2e-46ed-85c5-5a11f9c34ade-u2"
    exit 1
fi

JOB_ID="$1"
ENDPOINT_ID="aj1jw0guu5uziz"

echo "Checking status for job: $JOB_ID"
echo "Endpoint: $ENDPOINT_ID"
echo "----------------------------------------"

# Check the job status
curl -s -X GET "https://api.runpod.ai/v2/$ENDPOINT_ID/status/$JOB_ID" \
    -H "Authorization: Bearer $RUNPOD_API_KEY" | jq '.'

echo ""
echo "Status check completed!"
