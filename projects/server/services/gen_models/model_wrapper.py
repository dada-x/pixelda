import logging
from defs import (
    ImageGenerationRequest,
    VideoGenerationRequest,
    ImageEditRequest,
    MusicGenerationRequest,
    GenerationResponse,
)

from services.gen_models.tongyi.tongyi_image_model import (
    tongyi_gen_single_image_task,
    tongyi_wait_single_image_task,
    tongyi_edit_single_image_task,
)
from services.gen_models.tongyi.tongyi_video_model import (
    tongyi_gen_animation_task,
    tongyi_wait_animation_task,
)
from services.gen_models.tongyi.tongyi_music_model import (
    tongyi_gen_abc_music,
)

from services.gen_models.doubao.doubao_image_model import (
    doubao_gen_single_image,
    doubao_edit_single_image,
)
from services.gen_models.doubao.doubao_video_model import (
    doubao_gen_animation_task,
    doubao_wait_animation_task,
)
from services.gen_models.doubao.doubao_music_model import (
    doubao_gen_abc_music,
)

logger = logging.getLogger(__name__)


class ModelRouter:
    @staticmethod
    def generate_image(request: ImageGenerationRequest) -> str:
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
    def generate_abc_music(request: MusicGenerationRequest) -> tuple[str, str]:
        model_type = request.model_type.lower()

        if model_type == "doubao":
            logger.info("Routing music generation to Doubao model")
            return ModelRouter._generate_abc_music_doubao(request)
        elif model_type == "tongyi":
            logger.info("Routing music generation to Tongyi model")
            return ModelRouter._generate_abc_music_tongyi(request)
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. Supported: tongyi, doubao"
            )

    @staticmethod
    def _generate_image_tongyi(request: ImageGenerationRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_gen_single_image_task(request)
        return tongyi_wait_single_image_task(task, request.api_key)

    @staticmethod
    def _generate_image_doubao(request: ImageGenerationRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        return doubao_gen_single_image(request)

    @staticmethod
    def _edit_image_tongyi(request: ImageEditRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_edit_single_image_task(request)
        return tongyi_wait_single_image_task(task, request.api_key)

    @staticmethod
    def _edit_image_doubao(request: ImageEditRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        return doubao_edit_single_image(request)

    @staticmethod
    def _generate_video_tongyi(request: VideoGenerationRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        task = tongyi_gen_animation_task(request)
        return tongyi_wait_animation_task(task, request.api_key)

    @staticmethod
    def _generate_video_doubao(request: VideoGenerationRequest) -> str:
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        task = doubao_gen_animation_task(request)
        return doubao_wait_animation_task(task, request.api_key)

    @staticmethod
    def _generate_abc_music_doubao(
        request: MusicGenerationRequest,
    ) -> tuple[str, str]:
        if not request.api_key:
            raise ValueError("API key is required for Doubao model")
        return doubao_gen_abc_music(request)

    @staticmethod
    def _generate_abc_music_tongyi(
        request: MusicGenerationRequest,
    ) -> tuple[str, str]:
        if not request.api_key:
            raise ValueError("API key is required for Tongyi model")
        return tongyi_gen_abc_music(request)


def generate_image(request: ImageGenerationRequest) -> str:
    return ModelRouter.generate_image(request)


def edit_image(request: ImageEditRequest) -> str:
    return ModelRouter.edit_image(request)


def generate_video(request: VideoGenerationRequest) -> str:
    return ModelRouter.generate_video(request)


def generate_music(request: MusicGenerationRequest) -> tuple[str, str]:
    return ModelRouter.generate_abc_music(request)
