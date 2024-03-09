import os

import cv2
import napari
import numpy as np
from magicgui import magicgui


def save_annotated_mask(viewer: napari.Viewer, data_path: str, ind: int):
    layer_name = f"mask{ind:04d}"
    mask = viewer.layers[layer_name].data
    save_path = os.path.join(data_path, "mask", f"frame_{ind}.npy")
    np.save(save_path, mask)
    viewer.close()


def add_image_mask_to_viewer(
    viewer: napari.Viewer, image: np.ndarray, mask: np.ndarray, ind: int, curren: bool
):

    image_layer = viewer.add_image(image, name=f"image{ind:04d}")
    mask_layer = viewer.add_labels(mask, name=f"mask{ind:04d}")
    mask_layer.mode = "PAINT"
    mask_layer.brush_size = 2
    mask_layer.opacity = 0.6

    resize_and_position_layer(image_layer, current)
    resize_and_position_layer(mask_layer, current)


def resize_and_position_layer(layer, current: bool):

    scale_factor = 0.85 if current else 0.35
    layer.scale = [scale_factor for _ in layer.scale]
    layer.translate = [-20 if not current else 30, -5 if not current else 20]


def change_layer_mask(viewer: napari.Viewer, mask: np.ndarray, ind: int):
    layer_name = f"mask{ind:04d}"
    viewer.layers[layer_name].data = mask


def toggle_modes(viewer: napari.Viewer, ind: int):

    modes = ["paint", "fill"]
    layer_name = f"mask{ind:04d}"
    current_mode = viewer.layers[layer_name].mode

    if current_mode in modes:
        next_mode_index = (modes.index(current_mode) + 1) % len(modes)
        next_mode = modes[next_mode_index]
    else:
        next_mode = modes[0]

    viewer.layers[layer_name].mode = next_mode
    print(f"Switched to {next_mode} mode")


def set_label_to(viewer: napari.Viewer, ind: int, label_value: int):
    layer_name = f"mask{ind:04d}"
    if layer_name in viewer.layers:
        layer = viewer.layers[layer_name]
        if isinstance(layer, napari.layers.Labels):
            layer.selected_label = label_value
            print(f"Switched to label: {label_value}")
        else:
            print(f"The layer '{layer_name}' is not a Labels layer.")
    else:
        print(f"No layer named '{layer_name}' found.")
