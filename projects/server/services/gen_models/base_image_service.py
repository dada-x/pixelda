from typing import Union, Optional
from abc import ABC, abstractmethod
import logging

from defs import ImageEditRequest, ImageGenerationRequest


class BaseImageService(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_request(
        self, request: Union[ImageGenerationRequest, ImageEditRequest]
    ) -> None:
        if not request.api_key:
            raise ValueError(f"API key is required for {self.__class__.__name__}")

    @abstractmethod
    def _build_generation_params(self, request: ImageGenerationRequest) -> dict:
        pass

    @abstractmethod
    def _build_edit_params(self, request: ImageEditRequest) -> dict:
        pass
