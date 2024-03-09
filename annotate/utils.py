import os

import cv2
import numpy as np


def generate_color_dict(n):
    """
    Generate a color dictionary for integers from 1 to n.

    :param n: The number of distinct integers.
    :return: A dictionary mapping each integer to a unique color.
    """
    np.random.seed(0)
    colors = {i: np.random.choice(range(256), size=3).tolist() for i in range(1, n + 1)}
    return colors


def apply_colored_mask(image, mask, opacity=0.5):
    mask_colored = np.zeros_like(image)

    colors = generate_color_dict(60)
    for value, color in colors.items():
        mask_colored[mask == value] = color

    if mask_colored.shape[:2] != image.shape[:2]:
        mask_colored = cv2.resize(mask_colored, (image.shape[1], image.shape[0]))

    # Blend the image and the colored mask
    return cv2.addWeighted(image, 1 - opacity, mask_colored, opacity, 0)


def create_video_from_images(
    image_folder,
    mask_folder,
    output_video="output_video.avi",
    frame_size=(192, 120),
    frame_rate=30,
):
    # Initialize the video writer
    fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Use the XVID codec
    video_writer = cv2.VideoWriter(output_video, fourcc, frame_rate, frame_size)

    # Get the list of image and mask files
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(".png")])
    mask_files = sorted([f for f in os.listdir(mask_folder) if f.endswith(".npy")])

    # Check if counts of images and masks are equal
    if len(image_files) != len(mask_files):
        print("Error: The number of images and masks do not match.")
        return

    # Process each image and corresponding mask
    for img_file, mask_file in zip(image_files, mask_files):
        img_path = os.path.join(image_folder, img_file)
        mask_path = os.path.join(mask_folder, mask_file)

        # Load image and mask
        image = cv2.imread(img_path)
        mask = np.load(mask_path)

        # Apply the mask as an overlay
        overlaid_image = apply_colored_mask(image, mask, opacity=0.5)

        # Write the frame to the video
        video_writer.write(overlaid_image)

    # Release the video writer
    video_writer.release()
    print("Video creation complete.")


def _visualise_masks(stimulus: str):
    from glob import glob

    os.environ[
        "LOCAL_DATA_PATH"
    ] = "/Users/mariafilippova/Anastasiia-Master-Project/data/Allen"
    masks_folder = os.path.join(
        os.environ["LOCAL_DATA_PATH"], stimulus, "manual_corrected_mask"
    )
    masks_paths = glob(os.path.join(masks_folder, "*.npy"))
    masks_folder_images = os.path.join(masks_folder, "mask_images")
    if not os.path.exists(masks_folder_images):
        os.makedirs(masks_folder_images)
    for mask_path in masks_paths:
        mask = np.load(mask_path)
        mask_colored = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)

        for value, color in colors.items():
            mask_colored[mask == value] = color

        cv2.imwrite(
            os.path.join(
                masks_folder_images, os.path.basename(mask_path).replace(".npy", ".png")
            ),
            mask_colored,
        )
