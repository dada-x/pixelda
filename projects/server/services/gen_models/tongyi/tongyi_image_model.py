from http import HTTPStatus
from typing import Optional, Any
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import urllib.request
import logging
from dashscope import ImageSynthesis

from services.gen_models.utils import download_from_url, handle_api_response
from defs import (
    DEFAULT_TONGYI_IMAGE_MODEL,
    ImageGenerationRequest,
)


logger = logging.getLogger(__name__)


def tongyi_gen_single_image_task(request: ImageGenerationRequest) -> Any:
    logger.info(f"Generating image with prompt: {request.prompt}")

    if not request.api_key:
        raise ValueError("API key is required")

    try:
        call_params = {
            "api_key": request.api_key,
            "model": DEFAULT_TONGYI_IMAGE_MODEL,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt or "",
            "n": 1,
            "size": request.size,
            "prompt_extend": False,
        }

        if request.seed > 0:
            call_params["seed"] = request.seed

        task = ImageSynthesis.async_call(**call_params)

        handle_api_response(task, "Image generation task creation")
        return task

    except Exception as e:
        logger.error(f"Failed to create image generation task: {str(e)}")
        raise


def tongyi_wait_single_image_task(task: Any, api_key: str) -> str:
    logger.info("Waiting for image task completion")

    try:
        response = ImageSynthesis.wait(
            task,
            api_key=api_key,
        )

        handle_api_response(response, "Image task completion")

        if response.output.results:
            result_url = response.output.results[0].url
            return download_from_url(result_url)
        else:
            raise Exception("No results found in completed task")

    except Exception as e:
        logger.error(f"Failed to complete image task: {str(e)}")
        raise
