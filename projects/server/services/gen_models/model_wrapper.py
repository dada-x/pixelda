import logging
from defs import ImageGenerationRequest, VideoGenerationRequest, ImageEditRequest

from services.gen_models.tongyi.tongyi_image_model import (
    tongyi_gen_single_image_task,
    tongyi_wait_single_image_task,
    tongyi_edit_single_image_task,
)
from services.gen_models.tongyi.tongyi_video_model import (
    tongyi_gen_animation_task,
    tongyi_wait_animation_task,
)

from services.gen_models.doubao.doubao_image_model import (
    doubao_gen_single_image,
    doubao_edit_single_image,
)
from services.gen_models.doubao.doubao_video_model import (
    doubao_gen_animation_task,
    doubao_wait_animation_task,
)

logger = logging.getLogger(__name__)


class ModelRouter:
    """Router class to handle different AI model providers"""

    @staticmethod
    def generate_image(request: ImageGenerationRequest) -> str:
        """Route image generation request to appropriate model"""
        model_type = request.model_type.lower()

        if model_type == "tongyi":
            logger.info("Routing image generation to Tongyi model")
            return ModelRouter._generate_image_tongyi(request)
        elif model_type == "doubao":
            logger.info("Routing image generation to Doubao model")
            return ModelRouter._generate_image_doubao(request)
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. Supported: tongyi, doubao"
            )

    @staticmethod
    def edit_image(request: ImageEditRequest) -> str:
        """Route image editing request to appropriate model"""
        model_type = request.model_type.lower()

        if model_type == "tongyi":
            logger.info("Routing image editing to Tongyi model")
            return ModelRouter._edit_image_tongyi(request)
        elif model_type == "doubao":
            logger.info("Routing image editing to Doubao model")
            return ModelRouter._edit_image_doubao(request)
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. Supported: tongyi, doubao"
            )

    @staticmethod
    def generate_video(request: VideoGenerationRequest) -> str:
        """Route video generation request to appropriate model"""
        model_type = request.model_type.lower()

        if model_type == "tongyi":
            logger.info("Routing video generation to Tongyi model")
            return ModelRouter._generate_video_tongyi(request)
        elif model_type == "doubao":
            logger.info("Routing video generation to Doubao model")
            return ModelRouter._generate_video_doubao(request)
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. Supported: tongyi, doubao"
            )

    @staticmethod
    def _generate_image_tongyi(request: ImageGenerationRequest) -> str:
        """Handle Tongyi image generation (async task-based)"""
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_gen_single_image_task(request)
        return tongyi_wait_single_image_task(task, request.api_key)

    @staticmethod
    def _generate_image_doubao(request: ImageGenerationRequest) -> str:
        """Handle Doubao image generation (synchronous)"""
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        return doubao_gen_single_image(request)

    @staticmethod
    def _edit_image_tongyi(request: ImageEditRequest) -> str:
        """Handle Tongyi image editing (async task-based)"""
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_edit_single_image_task(request)
        return tongyi_wait_single_image_task(task, request.api_key)

    @staticmethod
    def _edit_image_doubao(request: ImageEditRequest) -> str:
        """Handle Doubao image editing (synchronous)"""
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        return doubao_edit_single_image(request)

    @staticmethod
    def _generate_video_tongyi(request: VideoGenerationRequest) -> str:
        """Handle Tongyi video generation (async task-based)"""
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_gen_animation_task(request)
        return tongyi_wait_animation_task(task, request.api_key)

    @staticmethod
    def _generate_video_doubao(request: VideoGenerationRequest) -> str:
        """Handle Doubao video generation (synchronous)"""
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        task = doubao_gen_animation_task(request)
        return doubao_wait_animation_task(task, request.api_key)


def generate_image(request: ImageGenerationRequest) -> str:
    """Generate image using model router"""
    return ModelRouter.generate_image(request)


def edit_image(request: ImageEditRequest) -> str:
    """Edit image using model router"""
    return ModelRouter.edit_image(request)


def generate_video(request: VideoGenerationRequest) -> str:
    """Generate video using model router"""
    return ModelRouter.generate_video(request)
