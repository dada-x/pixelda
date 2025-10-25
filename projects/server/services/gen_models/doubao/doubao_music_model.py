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
    GenerationResponse,
    MusicGenerationRequest,
)
from services.utils.music_tools import (
    write_abc_notation_to_file,
    cache_abc_to_file,
    midi_to_chiptune_wav,
)
from services.gen_models.base_service import BaseMusicService

logger = logging.getLogger(__name__)

with open(
    os.path.join(os.path.dirname(__file__), "..", "docs", "abc_notation.md"),
    "r",
    encoding="utf-8",
) as f:
    instruction = f.read()
    MUSIC_SYSTEM_PROMPT = f"You are a helpful assistant. You can generate creative and original music based on the input requirements given to you, and response strictly with ABC format. Use below instruction for ABC format:\n\n{instruction}"


MUSIC_GEN_PROMPT = """
Generate ABC notation of a piano song with ABC format, following requirements: 
duration: around {duration} seconds.
genre: {genre}.
tempo: {tempo}.
description: {description}.
return json object with keys:
- notation(pure ABC notation)
- comments(any comments)
"""


class TempChatResponse(BaseModel):
    notation: str
    comments: str


class DoubaoMusicService(BaseMusicService):

    def __init__(self):
        super().__init__()
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"

    def _create_client(self, api_key: str) -> Ark:
        return Ark(
            base_url=self.base_url,
            api_key=api_key,
        )

    def _build_generation_params(
        self, request: MusicGenerationRequest
    ) -> Dict[str, Any]:
        params = {
            "model": DEFAULT_DOUBAO_CHAT_MODEL,
            "max_tokens": DEFAULT_TEXT_ENGINE_MAX_TOKENS,
            "presence_penalty": 2,
            # "temperature": 0.5,
            "messages": [
                {"role": "system", "content": MUSIC_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": MUSIC_GEN_PROMPT.format(
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
    ) -> str:
        try:
            response = client.beta.chat.completions.parse(**params)

            if isinstance(response, ParsedChatCompletion):
                notation = cast(
                    TempChatResponse, response.choices[0].message.parsed
                ).notation
                cache_abc_to_file(notation)
                mid_file = write_abc_notation_to_file(notation)
                return midi_to_chiptune_wav(mid_file)
            else:
                raise TypeError("Response is not compatible with ChatCompletion")

        except Exception as e:
            self.logger.error(f"Failed to complete {operation.lower()}: {str(e)}")
            raise

    def generate_music(self, request: MusicGenerationRequest, operation: str) -> str:
        self._validate_request(request)
        assert request.api_key is not None

        client = self._create_client(request.api_key)
        params = self._build_generation_params(request)
        result = self._execute_request(client, params, operation)

        return result


_service = DoubaoMusicService()


def doubao_gen_abc_music(request: MusicGenerationRequest) -> str:
    _service.logger.info(f"Generating music with prompt: {request.prompt}")
    return _service.generate_music(request, "Music generation")
