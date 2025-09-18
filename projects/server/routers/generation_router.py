from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
import asyncio
import logging
import os
from defs import (
    ImageGenerationRequest,
    VideoGenerationRequest,
    FrameSplitRequest,
    FrameSplitResponse,
    GenerationResponse,
    ZipFramesRequest,
    ImageEditRequest,
)
from services.gen_models.model_wrapper import ModelRouter
from services.frame import process_split_frames, zip_frames

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/image", response_model=GenerationResponse)
async def generate_image(
    request: ImageGenerationRequest, x_api_key: str = Header(None, alias="X-API-Key")
):
    logger.info(f"Generating image with prompt: {request.prompt}")

    if x_api_key:
        request.api_key = x_api_key
    elif not request.api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is required. Provide it in X-API-Key header or request body.",
        )

    try:
        result = await asyncio.to_thread(
            ModelRouter.generate_image,
            request,
        )

        if not result:
            raise HTTPException(status_code=500, detail="No result URL returned")

        response_task_id = request.task_id
        if not response_task_id:
            response_task_id = (
                f"img_{request.prompt[:20].replace(' ', '_')}_{request.model_type}"
            )

        logger.info(f"Image generated successfully: {result}")
        return GenerationResponse(url=result, task_id=response_task_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


@router.post("/edit/image", response_model=GenerationResponse)
async def edit_image(
    request: ImageEditRequest, x_api_key: str = Header(None, alias="X-API-Key")
):
    logger.info(f"Editing image with prompt: {request.prompt}")

    if x_api_key:
        request.api_key = x_api_key
    elif not request.api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is required. Provide it in X-API-Key header or request body.",
        )

    if not request.image_url:
        raise HTTPException(
            status_code=400,
            detail="Base image URL is required for image editing.",
        )

    try:
        result = await asyncio.to_thread(
            ModelRouter.edit_image,
            request,
        )

        if not result:
            raise HTTPException(status_code=500, detail="No result URL returned")

        response_task_id = request.task_id
        if not response_task_id:
            response_task_id = (
                f"edit_{request.prompt[:20].replace(' ', '_')}_{request.model_type}"
            )

        logger.info(f"Image edited successfully: {result}")
        return GenerationResponse(url=result, task_id=response_task_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error editing image: {str(e)}")


@router.post("/generate/video", response_model=GenerationResponse)
async def generate_video(
    request: VideoGenerationRequest, x_api_key: str = Header(None, alias="X-API-Key")
):
    logger.info(f"Generating video with prompt: {request.prompt}")

    if x_api_key:
        request.api_key = x_api_key
    elif not request.api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is required. Provide it in X-API-Key header or request body.",
        )

    try:
        result = await asyncio.to_thread(
            ModelRouter.generate_video,
            request,
        )

        if not result:
            raise HTTPException(status_code=500, detail="No result URL returned")

        response_task_id = request.task_id
        if not response_task_id:
            response_task_id = (
                f"vid_{request.prompt[:20].replace(' ', '_')}_{request.model_type}"
            )

        logger.info(f"Video generated successfully: {result}")
        return GenerationResponse(url=result, task_id=response_task_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating video: {str(e)}")


@router.post("/generate/video_split_frames", response_model=FrameSplitResponse)
async def split_video_frames(request: FrameSplitRequest):
    logger.info(f"Splitting video frames for task: {request.task_id}")

    try:
        result = await asyncio.to_thread(process_split_frames, request)

        if not result or "frames" not in result:
            raise HTTPException(status_code=500, detail="No frames returned")

        frame_urls = result["frames"]
        if not frame_urls:
            raise HTTPException(status_code=500, detail="No frames were extracted")

        logger.info(
            f"Video frames split successfully. Generated {len(frame_urls)} frames"
        )
        return FrameSplitResponse(frames=frame_urls, task_id=request.task_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error splitting video frames: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error splitting video frames: {str(e)}"
        )


@router.post("/frames/zip")
async def zip_frames_endpoint(request: ZipFramesRequest):
    logger.info(
        f"Zipping {len(request.frame_urls)} frames with name: {request.name}, removebg: {request.removebg}"
    )

    try:
        zip_path = await asyncio.to_thread(
            zip_frames, request.frame_urls, request.name, request.removebg
        )

        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Zip file was not created")

        logger.info(f"Frames zipped successfully: {zip_path}")
        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type="application/zip",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error zipping frames: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error zipping frames: {str(e)}")
