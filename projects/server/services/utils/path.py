import os
from datetime import datetime
import base64
import mimetypes
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

DEFAULT_BASE_URL = "http://localhost:8000"


def get_project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


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


def get_cache_file_path(file_name: str, subfolder: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_dir = get_cache_folder()
    if subfolder:
        cache_dir = os.path.join(cache_dir, subfolder)
        os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{timestamp}_{file_name}")


def get_cache_file_path_from_url(url: str) -> str:
    cache_dir = get_cache_folder()
    os.makedirs(cache_dir, exist_ok=True)
    file_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
    return os.path.join(cache_dir, file_name)


def encode_file(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("not supported file type")
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"


def get_base_url() -> str:
    return os.getenv("BASE_URL", DEFAULT_BASE_URL)
