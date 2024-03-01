import json
import os
import sys

import cv2
import numpy as np
import pycocotools.mask
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry


def decode_compressed_rle(rle_object: dict) -> np.ndarray:
    """
    Decodes a single RLE object into a 2D binary mask.
    """
    return pycocotools.mask.decode(rle_object)


def decode_compressed_rle_frame(annotations: list) -> np.ndarray:

    masks = []
    for annotation in annotations:
        rle_object = annotation["segmentation"]
        mask = decode_compressed_rle(rle_object)
        masks.append(mask)

    return np.array(masks)


def decode_compressed_rle_video(annotations_video: list) -> list:

    masks = []
    for i, annotations_frame in enumerate(annotations_video):
        masks.append(decode_compressed_rle_frame(annotations_frame))

    return masks


class SegmentationModel:
    _instance = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(
        self,
        model_type="vit_h",
        checkpoint_path="sam_vit_h_4b8939.pth",
        device="cuda:1",
        amg_kwargs={},
    ):

        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        _ = sam.to(device=device)
        self.model = SamAutomaticMaskGenerator(
            sam, output_mode="coco_rle", **amg_kwargs
        )

    @staticmethod
    def save_masks(save_path, masks):

        save_path = os.path.join(save_path)

        with open(save_path, "w") as f:
            json.dump(masks, f)

        print("Saved masks to {}".format(save_path))

    def extract_masks(self, image_path):
        print(f"Loading image from {image_path}")

        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        masks = self.model.generate(image)

        return masks
