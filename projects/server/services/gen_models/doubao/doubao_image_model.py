import os
from volcenginesdkarkruntime import Ark
import logging
from defs import DEFAULT_DOUBAO_IMAGE_MODEL, ImageGenerationRequest
from services.gen_models.utils import download_from_url

logger = logging.getLogger(__name__)


def doubao_gen_single_image(request: ImageGenerationRequest) -> str:
    logger.info(f"Generating image with prompt: {request.prompt}")

    if not request.api_key:
        raise ValueError("API key is required")

    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=request.api_key,
    )

    try:
        call_params = {
            "model": DEFAULT_DOUBAO_IMAGE_MODEL,
            "prompt": request.prompt,
            "size": request.size.replace("*", "x"),
            "watermark": False,
        }

        if request.seed > 0:
            call_params["seed"] = request.seed

        response = client.images.generate(**call_params)

        if response.data:
            result_url = response.data[0].url
            return download_from_url(result_url)
        else:
            raise Exception("No results found in completed task")

    except Exception as e:
        logger.error(f"Failed to complete image task: {str(e)}")
        raise
