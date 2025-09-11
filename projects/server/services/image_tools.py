import os
import numpy as np
from rembg import remove, new_session
import cv2

from services.path import get_cache_folder

cache_dir = os.path.join(get_cache_folder(), "transparent_images")
os.makedirs(cache_dir, exist_ok=True)


def remove_solid_background(image_path: str, file_name: str) -> str:
    input = cv2.imread(image_path)
    session = new_session("isnet-anime")
    if input is None:
        raise ValueError(f"Could not load image from path: {image_path}")

    output_path = os.path.join(cache_dir, file_name)
    output = remove(input, session=session, alpha_matting=True)

    if isinstance(output, np.ndarray):
        output_array = output
    else:
        output_array = np.array(output)

    cv2.imwrite(output_path, output_array)

    return output_path
