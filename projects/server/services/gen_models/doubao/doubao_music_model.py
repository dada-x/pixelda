from abc import ABC
import os
from typing import Dict, Any, Union, cast
from pydantic import BaseModel
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.chat import ParsedChatCompletion
import logging

from defs import (
    DEFAULT_DOUBAO_CHAT_MODEL,
    DEFAULT_TEXT_ENGINE_MAX_TOKENS,
    MUSIC_SYSTEM_PROMPT,
    MUSIC_GEN_PROMPT,
    GenerationResponse,
    MusicGenerationRequest,
    TempChatResponse,
    MusicGenerationRequest,
)
from services.utils.music_tools import (
    to_original_wav,
    cache_abc_to_file,
    to_chiptune_wav,
)
from services.gen_models.base_service import BaseMusicService

logger = logging.getLogger(__name__)


class DoubaoMusicService(BaseMusicService):

    def __init__(self):
        super().__init__()
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = DEFAULT_DOUBAO_CHAT_MODEL
        self.max_tokens = DEFAULT_TEXT_ENGINE_MAX_TOKENS
        self.system_prompt = MUSIC_SYSTEM_PROMPT
        self.user_prompt_template = MUSIC_GEN_PROMPT

    def _create_client(self, api_key: str) -> Ark:
        return Ark(
            base_url=self.base_url,
            api_key=api_key,
        )

    def _build_generation_params(
        self, request: MusicGenerationRequest
    ) -> Dict[str, Any]:
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "presence_penalty": 2,
            "temperature": 2,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self.user_prompt_template.format(
                        duration=request.duration,
                        genre=request.genre,
                        tempo=request.tempo,
                        description=request.prompt,
                    ),
                },
            ],
            "response_format": TempChatResponse,
        }

        # not supported for doubao
        # if request.seed and request.seed > 0:
        #     params["seed"] = request.seed

        return params

    def _execute_request(
        self, client: Ark, params: Dict[str, Any], operation: str
    ) -> tuple[str, str]:
        try:
            response = client.beta.chat.completions.parse(**params)

            if isinstance(response, ParsedChatCompletion):
                notation = cast(
                    TempChatResponse, response.choices[0].message.parsed
                ).notation
                if notation is None:
                    raise ValueError("empty notation")
                notation = "\n".join(
                    [line for line in notation.splitlines() if line.strip() != ""]
                )

                cache_abc_to_file(notation)
                return (to_original_wav(notation), to_chiptune_wav(notation))
            else:
                raise TypeError("Response is not compatible with ChatCompletion")

        except Exception as e:
            self.logger.error(f"Failed to complete {operation.lower()}: {str(e)}")
            raise

    def generate_music(
        self, request: MusicGenerationRequest, operation: str
    ) -> tuple[str, str]:
        self._validate_request(request)
        assert request.api_key is not None

        client = self._create_client(request.api_key)
        params = self._build_generation_params(request)
        result = self._execute_request(client, params, operation)

        return result


_service = DoubaoMusicService()


def doubao_gen_abc_music(request: MusicGenerationRequest) -> tuple[str, str]:
    _service.logger.info(f"Generating music with prompt: {request.prompt}")
    return _service.generate_music(request, "Music generation")
