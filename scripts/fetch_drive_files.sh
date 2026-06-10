#!/bin/bash

# Source .env for GOOGLE_ACCESS_TOKEN
set -a
source "$(dirname "$0")/../.env"
set +a

if [ -z "$GOOGLE_ACCESS_TOKEN" ]; then
  echo "Error: GOOGLE_ACCESS_TOKEN not set in .env"
  exit 1
fi

FOLDER_ID="$1"
MIME_TYPE="${2:-image/png}"
OUTPUT_FILE="${3:-/tmp/drive_files.json}"

if [ -z "$FOLDER_ID" ]; then
  echo "Usage: $0 <folder_id> [mime_type] [output_file]"
  echo "Example: $0 10B_Q3rCwhpDwZzluaK1x9uliyQyjvK4r image/png /tmp/w22_files.json"
  exit 1
fi

echo "Fetching files from folder: $FOLDER_ID"
echo "Mime type: $MIME_TYPE"
echo "Output: $OUTPUT_FILE"

curl -s "https://www.googleapis.com/drive/v3/files?q='${FOLDER_ID}'%20in%20parents%20and%20mimeType%3D'${MIME_TYPE}'&fields=files(id,name)&pageSize=100&access_token=${GOOGLE_ACCESS_TOKEN}" | jq . > "$OUTPUT_FILE"

echo "Done. Results saved to $OUTPUT_FILE"
