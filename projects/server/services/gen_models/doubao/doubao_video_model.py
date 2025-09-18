from typing import Any
import time
from volcenginesdkarkruntime import Ark
import logging
from services.gen_models.utils import download_from_url
from services.gen_models.base_video_service import BaseVideoService
from defs import DEFAULT_DOUBAO_VIDEO_MODEL, VideoGenerationRequest


logger = logging.getLogger(__name__)


class DoubaoVideoService(BaseVideoService):

    def __init__(self):
        super().__init__()
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = DEFAULT_DOUBAO_VIDEO_MODEL

    def _create_client(self, api_key: str) -> Ark:
        return Ark(base_url=self.base_url, api_key=api_key)

    def _create_task(self, request: VideoGenerationRequest) -> str:
        self._validate_request(request)
        assert request.api_key is not None

        client = self._create_client(request.api_key)

        try:
            content = [
                {
                    "text": f"{request.prompt} --rs {request.resolution}",
                    "type": "text",
                },
                {
                    "image_url": {"url": request.base_image_url},
                    "type": "image_url",
                },
            ]

            task = client.content_generation.tasks.create(
                model=self.model, content=content
            )

            return task.id

        except Exception as e:
            self.logger.error(f"Failed to create video generation task: {str(e)}")
            raise

    def _wait_for_completion(self, task_id: str, api_key: str) -> str:
        client = self._create_client(api_key)

        try:
            response = client.content_generation.tasks.get(task_id=task_id)

            while response.status not in ["succeeded", "failed"]:
                time.sleep(5)
                response = client.content_generation.tasks.get(task_id=task_id)

            if hasattr(response.content, "video_url") and response.content.video_url:
                return download_from_url(response.content.video_url)
            else:
                raise Exception("No video URL found in completed task")

        except Exception as e:
            self.logger.error(f"Failed to complete video task: {str(e)}")
            raise


_service = DoubaoVideoService()


def doubao_gen_animation_task(request: VideoGenerationRequest) -> Any:
    _service.logger.info(f"Generating video with prompt: {request.prompt}")
    return _service._create_task(request)


def doubao_wait_animation_task(task: Any, api_key: str) -> str:
    _service.logger.info("Waiting for video task completion")
    return _service._wait_for_completion(task, api_key)
