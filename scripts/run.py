import sys

sys.path.append("..")

import argparse
import glob
import os

from utils import SegmentationModel

parser = argparse.ArgumentParser(description="Run the segmentation model")
parser.add_argument(
    "--device", type=str, default="cuda", help="Device to run the model on"
)
parser.add_argument("--data_path", type=str)

args = parser.parse_args()

model = SegmentationModel.get_instance(
    checkpoint_path="../sam_vit_h_4b8939.pth", device="cuda"
)
save_folder = os.path.join(args.data_path, "masks")
os.makedirs(save_folder, exist_ok=True)

image_paths = glob.glob(f"{args.data_path}/*.png")

for image_path in image_paths:

    print(f"Processing {image_path}")
    masks = model.extract_masks(image_path)
    base_name = os.path.basename(image_path).split(".")[0] + ".json"
    save_path = os.path.join(save_folder, base_name)
    model.save_masks(save_path, masks)
