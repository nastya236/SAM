import argparse
import glob
import os

import cv2
import napari
import numpy as np
from magicgui import magicgui

from src.helper import (
    add_image_mask_to_viewer,
    change_layer_mask,
    save_annotated_mask,
    set_label_to,
    toggle_modes,
)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument(
        "--step",
        type=int,
        default=1,
        help="Step between frames, 30 = 1 frame per 30 seconds",
    )

    args = parser.parse_args()
    os.makedirs(os.path.join(args.data_path, "masks"), exist_ok=True)

    image_paths = sorted(glob.glob(os.path.join(args.data_path, "frames", "*")))
    image_ids = np.arange(0, len(image_paths), args.step)

    for i, current_id in enumerate(image_ids):
        image = cv2.imread(image_paths[current_id])
        if i == 0:
            previous_id = current_id
            mask = np.ones(image.shape[:2], dtype=np.uint8)
        
        else:
            previous_id = current_id - args.step
            mask = np.load(
                os.path.join(
                    args.data_path, "masks", f"frame_{image_ids[previous_id]}.npy"
                )
            )
        viewer = napari.Viewer()

        image_layer = viewer.add_image(image, name=f"image{current_id:04d}")
        mask_layer = viewer.add_labels(mask, name=f"mask{current_id:04d}")

        save_button = magicgui(
            save_annotated_mask,
            call_button="Save",
            viewer={"visible": False, "value": viewer},
            data_path={"value": args.data_path},
            ind={"value": current_id},
        )

        previous_mask_button = magicgui(
            change_layer_mask,
            call_button="Apply previous",
            viewer={"visible": False, "value": viewer},
            mask={"value": mask},
            ind={"value": current_id},
        )

        viewer.window.add_dock_widget(save_button)
        viewer.window.add_dock_widget(previous_mask_button)

        napari.run()
