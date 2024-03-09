#!/bin/bash

VIDEO_DIR="../data/videos"

mkdir -p "$VIDEO_DIR"
for video in "$VIDEO_DIR"/*.mp4; do
  [[ -e "$video" ]] || continue

  base_name=$(basename "$video" .mp4)
  output_dir="../data/$base_name/frames"

  mkdir -p "$output_dir"

  duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video")
  duration=${duration%.*} 

  echo "Extracting frames from $video to $output_dir"

  for ((i=0; i<=$duration; i+=$2)); do
    ffmpeg -ss $i -i "$video" -frames:v 1 "$output_dir/frame_$(printf "%04d" $i).png"
  done
done
