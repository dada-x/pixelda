from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import urllib.request
import logging
from services.path import get_cache_file_path

logger = logging.getLogger(__name__)


def download_from_url(url: str) -> str:
    file_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
    cache_path = get_cache_file_path(file_name)
    urllib.request.urlretrieve(url, cache_path)

    logger.info(f"downloaded to: {cache_path}")
    return url


def handle_api_response(task_or_response, operation: str) -> None:
    if task_or_response.status_code == HTTPStatus.OK:
        logger.info(f"{operation} successful: {task_or_response.output}")
    else:
        error_msg = f"{operation} failed - Status: {task_or_response.status_code}, Code: {task_or_response.code}, Message: {task_or_response.message}"
        logger.error(error_msg)
        raise Exception(error_msg)
