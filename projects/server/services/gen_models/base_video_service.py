from typing import Union
from abc import ABC, abstractmethod
import logging

from defs import VideoGenerationRequest


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
