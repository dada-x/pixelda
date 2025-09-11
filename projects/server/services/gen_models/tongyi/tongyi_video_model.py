from typing import Any
from urllib.parse import unquote, urlparse
from dashscope import VideoSynthesis
import logging
from services.gen_models.utils import download_from_url, handle_api_response
from defs import (
    DEFAULT_TONGYI_VIDEO_MODEL,
    VideoGenerationRequest,
)


logger = logging.getLogger(__name__)


def tongyi_gen_animation_task(request: VideoGenerationRequest) -> Any:
    logger.info(f"Generating video with prompt: {request.prompt}")

    if not request.api_key:
        raise ValueError("API key is required")

    try:
        task = VideoSynthesis.async_call(
            api_key=request.api_key,
            model=DEFAULT_TONGYI_VIDEO_MODEL,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            img_url=request.base_image_url,
            resolution=request.resolution,
            prompt_extend=False,
        )

        handle_api_response(task, "Video generation task creation")
        return task

    except Exception as e:
        logger.error(f"Failed to create video generation task: {str(e)}")
        raise


def tongyi_wait_animation_task(task: Any, api_key: str) -> str:
    logger.info("Waiting for video task completion")

    try:
        response = VideoSynthesis.wait(
            task,
            api_key=api_key,
        )

        handle_api_response(response, "Video task completion")

        if hasattr(response.output, "video_url") and response.output.video_url:
            return download_from_url(response.output.video_url)
        else:
            raise Exception("No video URL found in completed task")

    except Exception as e:
        logger.error(f"Failed to complete video task: {str(e)}")
        raise
