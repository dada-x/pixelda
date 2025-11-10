import os
import numpy as np
from rembg import remove, new_session
import cv2
import logging
from PIL import Image

from services.utils.path import get_cache_folder

logger = logging.getLogger(__name__)

cache_dir = os.path.join(get_cache_folder(), "transparent_images")
os.makedirs(cache_dir, exist_ok=True)


def remove_solid_background(image_path: str, file_name: str) -> str:
    input = cv2.imread(image_path)
    session = new_session("u2net")
    if input is None:
        raise ValueError(f"Could not load image from path: {image_path}")

    output_path = os.path.join(cache_dir, file_name)
    output = remove(input, session=session, alpha_matting=False)

    if isinstance(output, np.ndarray):
        output_array = output
    else:
        output_array = np.array(output)

    if output_array.dtype != np.uint8:
        output_array = output_array.astype(np.uint8)

    original_h, original_w = input.shape[:2]
    processed_h, processed_w = output_array.shape[:2]

    if (processed_h, processed_w) != (original_h, original_w):
        logger.info(
            f"Background removal changed dimensions from {original_w}x{original_h} to {processed_w}x{processed_h}"
        )

        if processed_h > original_h or processed_w > original_w:
            output_array = cv2.resize(output_array, (original_w, original_h))
            logger.info(f"Resized processed image back to {original_w}x{original_h}")
        else:
            padded = np.zeros(
                (original_h, original_w, output_array.shape[2]), dtype=np.uint8
            )
            if output_array.shape[2] == 4:
                padded[:, :, 3] = 0
            y_offset = (original_h - processed_h) // 2
            x_offset = (original_w - processed_w) // 2
            padded[
                y_offset : y_offset + processed_h, x_offset : x_offset + processed_w
            ] = output_array
            output_array = padded

    success = cv2.imwrite(output_path, output_array)
    if not success:
        raise ValueError(f"Failed to save processed image to {output_path}")

    return output_path


def merge_frames_to_sprite(image_paths: list[str], output_path: str) -> str:
    if not image_paths:
        raise ValueError("No image paths provided")

    images = []
    for path in image_paths:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Could not load image from path: {path}")
        logger.info(f"Loaded image {path}: shape {img.shape}, dtype {img.dtype}")
        images.append(img)

    if not images:
        raise ValueError("No valid images found")

    heights = [img.shape[0] for img in images]
    widths = [img.shape[1] for img in images]
    channels = [img.shape[2] if len(img.shape) > 2 else 1 for img in images]

    logger.info(f"Image heights: {heights}, widths: {widths}, channels: {channels}")

    if len(set(heights)) != 1:
        raise ValueError(
            f"All images must have the same height for horizontal merging. Heights found: {heights}"
        )

    has_alpha = any(ch == 4 for ch in channels)
    target_channels = 4 if has_alpha else 3

    logger.info(f"Target channels: {target_channels} (has_alpha: {has_alpha})")

    processed_images = []
    for i, img in enumerate(images):
        if len(img.shape) == 2:
            if target_channels == 4:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 1:
            if target_channels == 4:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 3 and target_channels == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        elif img.shape[2] == 4 and target_channels == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        if img.dtype != np.uint8:
            img = img.astype(np.uint8)

        processed_images.append(img)
        logger.info(f"Processed image {i}: shape {img.shape}, dtype {img.dtype}")

    try:
        merged = np.concatenate(processed_images, axis=1)
        logger.info(f"Merged image shape: {merged.shape}, dtype: {merged.dtype}")

        try:
            if merged.shape[2] == 4:
                merged_rgba = cv2.cvtColor(merged, cv2.COLOR_BGRA2RGBA)
                if merged_rgba.dtype != np.uint8:
                    merged_rgba = merged_rgba.astype(np.uint8)
                pil_image = Image.fromarray(merged_rgba, "RGBA")
            else:
                merged_rgb = cv2.cvtColor(merged, cv2.COLOR_BGR2RGB)
                if merged_rgb.dtype != np.uint8:
                    merged_rgb = merged_rgb.astype(np.uint8)
                pil_image = Image.fromarray(merged_rgb, "RGB")

            pil_image.save(output_path, "PNG")
            logger.info(f"Successfully saved merged image to {output_path} using PIL")
        except (NameError, ImportError):
            logger.warning("PIL not available, falling back to OpenCV for image saving")
            success = cv2.imwrite(output_path, merged)
            if not success:
                raise ValueError(f"Failed to save merged image to {output_path}")
            logger.info(
                f"Successfully saved merged image to {output_path} using OpenCV"
            )
    except Exception as e:
        logger.error(f"Error during image merging: {str(e)}")
        raise ValueError(f"Error during image merging: {str(e)}")

    return output_path
