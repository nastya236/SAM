import argparse
import glob
import os

import cv2
import napari
import numpy as np
from magicgui import magicgui

from SAM.annotate.helper import (
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
        default=30,
        help="Step between frames, 30 = 1 frame per 30 seconds",
    )

    args = parser.parse_args()

    image_paths = sorted(glob.glob(os.path.join(args.data_path, "raw", "*")))
    image_ids = np.arange(0, len(image_paths), args.step)

    for i, current_id in enumerate(image_ids):
        current_image = cv2.imread(image_paths[current_id])

        if i == 0:
            previous_image = current_image
            previous_mask = np.zeros_like(current_image)
        else:
            previous_id = current_id - args.step
            previous_image = cv2.imread(image_paths[image_ids[previous_id]])
            previous_mask = np.load(
                os.path.join(
                    args.data_path, "masks", f"frame_{image_ids[previous_id]}.npy"
                )
            )

        viewer = napari.Viewer()
        add_image_mask_to_viewer(
            viewer, previous_image, previous_mask, ind=previous_id, current=0
        )

        add_image_mask_to_viewer(
            viewer, current_image, current_mask, ind=current_id, current=1
        )

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
            mask={"value": previous_mask},
            ind={"value": current_id},
        )

        # viewer.bind_key(
        #     'Control-D',
        #     lambda event: toggle_modes(viewer, instance['image_id']))

        # for label in range(8):
        #     viewer.bind_key(f'Control-{label}',
        #                     lambda event, lbl=label: set_label_to(
        #                         viewer, instance['image_id'], lbl))

        viewer.window.add_dock_widget(save_button)
        viewer.window.add_dock_widget(previous_mask_button)

        napari.run()
