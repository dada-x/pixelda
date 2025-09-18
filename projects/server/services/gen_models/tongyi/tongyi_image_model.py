from http import HTTPStatus
from typing import Optional, Any, Dict, Union
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import urllib.request
import logging
from dashscope import ImageSynthesis

from services.gen_models.utils import download_from_url, handle_api_response
from services.gen_models.base_image_service import BaseImageService
from defs import (
    DEFAULT_TONGYI_EDIT_FUNCTION,
    DEFAULT_TONGYI_EDIT_IMAGE_MODEL,
    DEFAULT_TONGYI_IMAGE_MODEL,
    ImageEditRequest,
    ImageGenerationRequest,
)

logger = logging.getLogger(__name__)


class TongyiImageService(BaseImageService):
    def __init__(self):
        super().__init__()
        self.edit_function = DEFAULT_TONGYI_EDIT_FUNCTION
        self.edit_model = DEFAULT_TONGYI_EDIT_IMAGE_MODEL
        self.generation_model = DEFAULT_TONGYI_IMAGE_MODEL

    def _build_generation_params(
        self, request: ImageGenerationRequest
    ) -> Dict[str, Any]:
        params = {
            "api_key": request.api_key,
            "model": self.generation_model,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt or "",
            "n": 1,
            "size": request.size,
            "prompt_extend": False,
        }

        if request.seed and request.seed > 0:
            params["seed"] = request.seed

        return params

    def _build_edit_params(self, request: ImageEditRequest) -> Dict[str, Any]:
        params = {
            "api_key": request.api_key,
            "model": self.edit_model,
            "function": self.edit_function,
            "base_image_url": request.image_url,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt or "",
            "n": 1,
            "size": request.size,
            "prompt_extend": False,
        }

        if request.seed and request.seed > 0:
            params["seed"] = request.seed

        return params

    def _create_task(self, params: Dict[str, Any], operation: str) -> Any:
        try:
            task = ImageSynthesis.async_call(**params)
            handle_api_response(task, f"{operation} task creation")
            return task
        except Exception as e:
            self.logger.error(f"Failed to create {operation.lower()} task: {str(e)}")
            raise

    def _wait_for_completion(self, task: Any, api_key: str, operation: str) -> str:
        try:
            response = ImageSynthesis.wait(task, api_key=api_key)
            handle_api_response(response, f"{operation} task completion")

            if not response.output.results:
                raise Exception("No results found in completed task")

            result_url = response.output.results[0].url
            return download_from_url(result_url)

        except Exception as e:
            self.logger.error(f"Failed to complete {operation.lower()} task: {str(e)}")
            raise


_service = TongyiImageService()


def tongyi_gen_single_image_task(request: ImageGenerationRequest) -> Any:
    _service.logger.info(f"Generating image with prompt: {request.prompt}")

    _service._validate_request(request)
    params = _service._build_generation_params(request)
    return _service._create_task(params, "Image generation")


def tongyi_edit_single_image_task(request: ImageEditRequest) -> Any:
    _service.logger.info(f"Editing image with prompt: {request.prompt}")

    _service._validate_request(request)
    if not request.image_url:
        raise ValueError("Image URL is required for editing")

    params = _service._build_edit_params(request)
    return _service._create_task(params, "Image editing")


def tongyi_wait_single_image_task(task: Any, api_key: str) -> str:
    _service.logger.info("Waiting for image task completion")
    return _service._wait_for_completion(task, api_key, "Image")
