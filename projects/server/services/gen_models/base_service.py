from typing import Union
from abc import ABC, abstractmethod
import logging

from defs import (
    MusicGenerationRequest,
    VideoGenerationRequest,
    ImageEditRequest,
    ImageGenerationRequest,
)


class BaseVideoService(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_request(self, request: VideoGenerationRequest) -> None:
        if not request.api_key:
            raise ValueError(f"API key is required for {self.__class__.__name__}")

    @abstractmethod
    def _create_task(self, request: VideoGenerationRequest) -> str:
        pass

    @abstractmethod
    def _wait_for_completion(self, task_id: str, api_key: str) -> str:
        pass


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


class BaseMusicService(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_request(
        self,
        request: Union[
            ImageGenerationRequest, ImageEditRequest, MusicGenerationRequest
        ],
    ) -> None:
        if not request.api_key:
            raise ValueError(f"API key is required for {self.__class__.__name__}")

    @abstractmethod
    def _build_generation_params(self, request: ImageGenerationRequest) -> dict:
        pass
