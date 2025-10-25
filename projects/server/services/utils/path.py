import os
from datetime import datetime
import base64
import mimetypes


def get_project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))


def get_cache_folder() -> str:
    output_folder = os.path.join(get_project_root(), "cache")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


def get_log_folder() -> str:
    log_folder = os.path.join(get_project_root(), "logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    return log_folder


def get_cache_file_path(file_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(get_cache_folder(), f"{timestamp}_{file_name}")


def encode_file(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("not supported file type")
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"
