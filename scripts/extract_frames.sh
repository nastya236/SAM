#!/bin/bash

# Directory containing video files
VIDEO_DIR="../data"

# Iterate over each video file in the VIDEO_DIR
for video in "$VIDEO_DIR"/*.mp4; do
  # Skip if no video files are found
  [[ -e "$video" ]] || continue

  # Extract filename without extension
  base_name=$(basename "$video" .mp4)

  # Create a directory for the current video file
  mkdir -p "$VIDEO_DIR/$base_name"

  echo "$VIDEO_DIR/$base_name"
  # Use ffmpeg to split video into frames and save in the created directory
  ffmpeg -i "$video" -vf fps=1 "$VIDEO_DIR/$base_name/frame-%04d.png"
done
