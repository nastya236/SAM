import argparse
import glob
import os
import cv2
import numpy as np
import napari
from magicgui import magicgui
from src.helper import (
    add_image_mask_to_viewer,
    save_annotated_mask,
    set_label_to,
    toggle_modes,
)


def get_image_and_mask_paths(data_path):
    """Get sorted lists of image and mask paths."""
    image_paths = sorted(glob.glob(os.path.join(data_path, "frames", "*")))
    mask_paths = sorted(glob.glob(os.path.join(data_path, "masks", "*")))
    return image_paths, mask_paths


def get_unlabeled_image_ids(image_paths, mask_paths):
    """Extracts IDs of images that do not have a corresponding mask."""
    extract_id = lambda path: int(os.path.basename(path).split("_")[1].split(".")[0])
    image_ids = list(map(extract_id, image_paths))
    mask_ids = list(map(extract_id, mask_paths))
    return sorted(list(set(image_ids) - set(mask_ids)))


def preprocess_image(image_path):
    """Reads and crops an image from the given path."""
    image = cv2.imread(image_path)[70:-300, 320:-500]
    return image


def create_or_load_mask(data_path, current_id, step):
    """Creates a new mask or loads an existing one based on the current ID."""
    if current_id == 0:
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
    else:
        previous_id = current_id - step
        mask_path = os.path.join(data_path, "masks", f"frame_{previous_id:04d}.npy")
        mask = np.load(mask_path)
    return mask


def setup_viewer(image, mask, current_id):
    """Sets up the napari viewer with the image and mask layers."""
    viewer = napari.Viewer()
    viewer.add_image(image, name=f"image{current_id:04d}")
    viewer.add_labels(mask, name=f"mask{current_id:04d}")
    return viewer


def add_save_button_to_viewer(viewer, data_path, current_id):
    """Adds a save button to the napari viewer."""
    save_button = magicgui(
        save_annotated_mask,
        call_button="Save",
        viewer={"visible": False, "value": viewer},
        data_path={"value": data_path},
        ind={"value": current_id},
    )
    viewer.window.add_dock_widget(save_button)


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
    os.makedirs(os.path.join(args.data_path, "cropped_frames"), exist_ok=True)

    image_paths, mask_paths = get_image_and_mask_paths(args.data_path)
    image_ids_unlabeled = get_unlabeled_image_ids(image_paths, mask_paths)

    for current_id in image_ids_unlabeled:
        image_path = os.path.join(
            args.data_path, "frames", f"frame_{current_id:04d}.png"
        )
        image = preprocess_image(image_path)
        cropped_path = os.path.join(
            args.data_path, "cropped_frames", f"frame_{current_id:04d}.png"
        )
        cv2.imwrite(cropped_path, image)

        mask = create_or_load_mask(args.data_path, current_id, args.step)

        viewer = setup_viewer(image, mask, current_id)
        add_save_button_to_viewer(viewer, args.data_path, current_id)

        napari.run()
