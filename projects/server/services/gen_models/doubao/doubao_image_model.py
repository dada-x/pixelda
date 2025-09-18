import os
from typing import Dict, Any, Union
from volcenginesdkarkruntime import Ark
import logging

from defs import DEFAULT_DOUBAO_IMAGE_MODEL, ImageEditRequest, ImageGenerationRequest
from services.gen_models.utils import download_from_url
from services.gen_models.base_image_service import BaseImageService

logger = logging.getLogger(__name__)


class DoubaoImageService(BaseImageService):

    def __init__(self):
        super().__init__()
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"

    def _create_client(self, api_key: str) -> Ark:
        return Ark(
            base_url=self.base_url,
            api_key=api_key,
        )

    def _build_generation_params(
        self, request: ImageGenerationRequest
    ) -> Dict[str, Any]:
        params = {
            "model": DEFAULT_DOUBAO_IMAGE_MODEL,
            "prompt": request.prompt,
            "size": request.size.replace("*", "x"),
            "watermark": False,
        }

        if request.seed and request.seed > 0:
            params["seed"] = request.seed

        return params

    def _build_edit_params(self, request: ImageEditRequest) -> Dict[str, Any]:
        params = {
            "model": DEFAULT_DOUBAO_IMAGE_MODEL,
            "prompt": request.prompt,
            "image": request.image_url,
            "size": request.size.replace("*", "x"),
            "watermark": False,
        }

        if request.seed and request.seed > 0:
            params["seed"] = request.seed

        return params

    def _execute_request(
        self, client: Ark, params: Dict[str, Any], operation: str
    ) -> str:
        try:
            response = client.images.generate(**params)

            if not response.data:
                raise Exception("No results found in completed task")

            result_url = response.data[0].url
            return download_from_url(result_url)

        except Exception as e:
            self.logger.error(f"Failed to complete {operation.lower()}: {str(e)}")
            raise

    def _process_generation_request(
        self, request: ImageGenerationRequest, operation: str
    ) -> str:
        self._validate_request(request)
        assert request.api_key is not None
        client = self._create_client(request.api_key)
        params = self._build_generation_params(request)
        return self._execute_request(client, params, operation)

    def _process_edit_request(self, request: ImageEditRequest, operation: str) -> str:
        self._validate_request(request)
        if not request.image_url:
            raise ValueError("Image URL is required for editing")

        assert request.api_key is not None
        client = self._create_client(request.api_key)
        params = self._build_edit_params(request)
        return self._execute_request(client, params, operation)


_service = DoubaoImageService()


def doubao_gen_single_image(request: ImageGenerationRequest) -> str:
    _service.logger.info(f"Generating image with prompt: {request.prompt}")
    return _service._process_generation_request(request, "Image generation")


def doubao_edit_single_image(request: ImageEditRequest) -> str:
    _service.logger.info(f"Editing image with prompt: {request.prompt}")
    return _service._process_edit_request(request, "Image editing")
