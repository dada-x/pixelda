import os
from attr import dataclass
from pydantic import BaseModel
from typing import Optional, List


DEFAULT_IMAGE_SIZE = "1024*1024"
DEFAULT_VIDEO_RESOLUTION = "480P"
DEFAULT_TONGYI_IMAGE_MODEL = "wan2.5-t2i-preview"
DEFAULT_TONGYI_EDIT_IMAGE_MODEL = "wanx2.1-imageedit"
DEFAULT_TONGYI_EDIT_FUNCTION = "description_edit"
DEFAULT_TONGYI_VIDEO_MODEL = "wan2.5-i2v-preview"
DEFAULT_DOUBAO_IMAGE_MODEL = "doubao-seedream-4-0-250828"
DEFAULT_DOUBAO_VIDEO_MODEL = "doubao-seedance-1-0-pro-250528"

DEFAULT_TEXT_ENGINE_MAX_TOKENS = 2048
DEFAULT_TONGYI_CHAT_MODEL = "qwen-plus"
DEFAULT_DOUBAO_CHAT_MODEL = "doubao-seed-1-6-251015"


class LazyPrompt:
    def __init__(self, file_path):
        self.file_path = file_path
        self._prompt = None

    def __str__(self):
        if self._prompt is None:
            with open(self.file_path, "r", encoding="utf-8") as f:
                instruction = f.read()
                self._prompt = f"You are a helpful assistant. You can generate creative and original music based on the input requirements given to you, and response strictly with ABC format. Use below instruction for ABC format:\n\n{instruction}"
        return self._prompt


MUSIC_SYSTEM_PROMPT = LazyPrompt(
    os.path.join(os.path.dirname(__file__), "assets", "abc_notation.md")
).__str__()

MUSIC_GEN_PROMPT = """
Generate ABC notation of a piano song with ABC format, following below requirements, and double check the format correctness with documentation:
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


class ImageGenerationRequest(BaseModel):
    api_key: Optional[str] = None
    prompt: str
    negative_prompt: str = ""
    seed: int = -1
    size: str = DEFAULT_IMAGE_SIZE
    task_id: Optional[str] = None
    model_type: str = "tongyi"


class ImageEditRequest(ImageGenerationRequest):
    image_url: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    api_key: Optional[str] = None
    base_image_url: str
    prompt: str
    negative_prompt: str = ""
    resolution: str = DEFAULT_VIDEO_RESOLUTION
    task_id: Optional[str] = None
    model_type: str = "tongyi"


class MusicGenerationRequest(BaseModel):
    api_key: Optional[str] = None
    prompt: str
    seed: int = -1
    duration: int = 30
    genre: str = "pop"
    tempo: str = "medium"
    task_id: Optional[str] = None
    model_type: str = "tongyi"


class FrameSplitRequest(BaseModel):
    task_id: str
    video_url: str
    from_time: float = 0.0
    to_time: float = 10.0
    count: int = 10


class ZipFramesRequest(BaseModel):
    name: str
    frame_urls: List[str]
    removebg: bool = False


class FrameSplitResponse(BaseModel):
    frames: List[str]
    task_id: str
    error_info: Optional[str] = None


class MusicResponse(BaseModel):
    original: str
    chiptune: str
    task_id: str
    error_info: Optional[str] = None


class GenerationResponse(BaseModel):
    url: str
    original_content: Optional[str] = None
    task_id: Optional[str] = None
    error_info: Optional[str] = None
