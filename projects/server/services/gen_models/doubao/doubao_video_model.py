from typing import Any
from urllib.parse import unquote, urlparse
from dashscope import VideoSynthesis
import logging
import time

from volcenginesdkarkruntime import Ark
from services.gen_models.utils import download_from_url
from defs import (
    DEFAULT_DOUBAO_VIDEO_MODEL,
    VideoGenerationRequest,
)


logger = logging.getLogger(__name__)


def doubao_gen_animation_task(request: VideoGenerationRequest) -> Any:
    logger.info(f"Generating video with prompt: {request.prompt}")

    if not request.api_key:
        raise ValueError("API key is required")

    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=request.api_key
    )

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
            model=DEFAULT_DOUBAO_VIDEO_MODEL, content=content
        )

        return task.id

    except Exception as e:
        logger.error(f"Failed to create video generation task: {str(e)}")
        raise


def doubao_wait_animation_task(task: Any, api_key: str) -> str:
    logger.info("Waiting for video task completion")

    client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=api_key)

    try:
        response = client.content_generation.tasks.get(
            task_id=task,
        )

        while response.status not in ["succeeded", "failed"]:
            time.sleep(5)
            response = client.content_generation.tasks.get(
                task_id=task,
            )

        if hasattr(response.content, "video_url") and response.content.video_url:
            return download_from_url(response.content.video_url)
        else:
            raise Exception("No video URL found in completed task")

    except Exception as e:
        logger.error(f"Failed to complete video task: {str(e)}")
        raise
