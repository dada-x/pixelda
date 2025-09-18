from pydantic import BaseModel
from typing import Optional, List


DEFAULT_IMAGE_SIZE = "1024*1024"
DEFAULT_VIDEO_RESOLUTION = "480P"
DEFAULT_TONGYI_IMAGE_MODEL = "wan2.2-t2i-flash"
DEFAULT_TONGYI_EDIT_IMAGE_MODEL = "wanx2.1-imageedit"
DEFAULT_TONGYI_EDIT_FUNCTION = "description_edit"
DEFAULT_TONGYI_VIDEO_MODEL = "wan2.2-i2v-flash"
DEFAULT_DOUBAO_IMAGE_MODEL = "doubao-seedream-4-0-250828"
DEFAULT_DOUBAO_VIDEO_MODEL = "doubao-seedance-1-0-pro-250528"


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


class GenerationResponse(BaseModel):
    url: str
    task_id: Optional[str] = None
    error_info: Optional[str] = None
