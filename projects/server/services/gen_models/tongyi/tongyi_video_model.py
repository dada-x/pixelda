from typing import Any
from dashscope import VideoSynthesis
import logging
from services.gen_models.utils import download_from_url, handle_api_response
from services.gen_models.base_video_service import BaseVideoService
from defs import DEFAULT_TONGYI_VIDEO_MODEL, VideoGenerationRequest


logger = logging.getLogger(__name__)


class TongyiVideoService(BaseVideoService):

    def __init__(self):
        super().__init__()
        self.model = DEFAULT_TONGYI_VIDEO_MODEL

    def _create_task(self, request: VideoGenerationRequest) -> Any:
        self._validate_request(request)
        assert request.api_key is not None

        try:
            task = VideoSynthesis.async_call(
                api_key=request.api_key,
                model=self.model,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt or "",
                img_url=request.base_image_url,
                resolution=request.resolution,
                prompt_extend=False,
            )

            handle_api_response(task, "Video generation task creation")
            return task

        except Exception as e:
            self.logger.error(f"Failed to create video generation task: {str(e)}")
            raise

    def _wait_for_completion(self, task: Any, api_key: str) -> str:
        try:
            response = VideoSynthesis.wait(task, api_key=api_key)
            handle_api_response(response, "Video task completion")

            if hasattr(response.output, "video_url") and response.output.video_url:
                return download_from_url(response.output.video_url)
            else:
                raise Exception("No video URL found in completed task")

        except Exception as e:
            self.logger.error(f"Failed to complete video task: {str(e)}")
            raise


_service = TongyiVideoService()


def tongyi_gen_animation_task(request: VideoGenerationRequest) -> Any:
    _service.logger.info(f"Generating video with prompt: {request.prompt}")
    return _service._create_task(request)


def tongyi_wait_animation_task(task: Any, api_key: str) -> str:
    _service.logger.info("Waiting for video task completion")
    return _service._wait_for_completion(task, api_key)
