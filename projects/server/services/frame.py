from pathlib import PurePosixPath
import os
import time
import cv2
import urllib.request
import logging
import zipfile
import tempfile
import shutil
from fastapi import HTTPException
from urllib.parse import unquote, urlparse
from typing import Optional

from services.path import get_cache_folder
from services.image_tools import remove_solid_background
from defs import FrameSplitRequest


logger = logging.getLogger(__name__)


DEFAULT_BASE_URL = "http://localhost:8000"
FRAMES_ENDPOINT = "frames"
FRAME_FILENAME_TEMPLATE = "frame_{:04d}.png"
FRAME_DIR_TEMPLATE = "{}_{}"


def get_base_url() -> str:
    """Get the base URL from environment or use default"""
    return os.getenv("BASE_URL", DEFAULT_BASE_URL)


def get_cache_path(url: str) -> str:
    cache_dir = get_cache_folder()
    os.makedirs(cache_dir, exist_ok=True)
    file_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
    logger.debug(f"Generated cache path: {os.path.join(cache_dir, file_name)}")
    return os.path.join(cache_dir, file_name)


def get_or_download_file(url: str) -> str:
    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        logger.info(f"File found in cache: {cache_path}")
        return cache_path

    logger.info(f"Downloading file to cache: {cache_path}")
    try:
        urllib.request.urlretrieve(url, cache_path)
        logger.info(f"File downloaded successfully: {cache_path}")
        return cache_path
    except Exception as e:
        logger.error(f"Failed to download file from {url}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to download file: {str(e)}"
        )


def create_frame_directory(task_id: str, cache_folder: str) -> tuple[str, str]:
    timestamp = int(time.time())
    frame_dir_name = FRAME_DIR_TEMPLATE.format(task_id, timestamp)
    frames_dir = os.path.join(cache_folder, FRAMES_ENDPOINT)
    frame_dir_path = os.path.join(frames_dir, frame_dir_name)
    os.makedirs(frame_dir_path, exist_ok=True)
    logger.info(f"Created frame directory: {frame_dir_path}")
    return frame_dir_path, frame_dir_name


def extract_frames_from_video(
    video_path: str, frame_interval: int, max_frames: int, frame_dir_path: str
) -> list[str]:
    logger.info(f"Starting frame extraction from video: {video_path}")
    logger.info(f"Frame interval: {frame_interval}, Max frames: {max_frames}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.error(f"Cannot open video file: {video_path}")
        raise HTTPException(status_code=500, detail="Cannot open video file")

    frames = []
    frame_index = 0
    extracted_count = 0

    try:
        while extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                logger.info(f"End of video reached. Extracted {extracted_count} frames")
                break

            if frame_index % frame_interval == 0:
                frame_filename = FRAME_FILENAME_TEMPLATE.format(extracted_count)
                frame_filepath = os.path.join(frame_dir_path, frame_filename)

                if not cv2.imwrite(frame_filepath, frame):
                    logger.warning(
                        f"Failed to save frame {extracted_count} to {frame_filepath}"
                    )
                    continue

                frames.append(frame_filename)
                extracted_count += 1
                logger.debug(f"Extracted frame {extracted_count}/{max_frames}")

            frame_index += 1
    finally:
        cap.release()
        logger.info(f"Video capture released. Total frames processed: {frame_index}")

    logger.info(f"Frame extraction completed. Extracted {len(frames)} frames")
    return frames


def extract_frames_at_timestamps(
    video_path: str, timestamps: list[float], frame_dir_path: str
) -> list[str]:
    logger.info(f"Starting timestamp-based frame extraction from video: {video_path}")
    logger.info(f"Timestamps: {timestamps}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.error(f"Cannot open video file: {video_path}")
        raise HTTPException(status_code=500, detail="Cannot open video file")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []

    try:
        for i, timestamp in enumerate(timestamps):
            frame_number = int(timestamp * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                logger.warning(
                    f"Could not read frame at timestamp {timestamp}s (frame {frame_number})"
                )
                continue

            frame_filename = FRAME_FILENAME_TEMPLATE.format(i)
            frame_filepath = os.path.join(frame_dir_path, frame_filename)

            if not cv2.imwrite(frame_filepath, frame):
                logger.warning(f"Failed to save frame {i} to {frame_filepath}")
                continue

            frames.append(frame_filename)
            logger.debug(f"Extracted frame {i+1}/{len(timestamps)} at {timestamp}s")

    finally:
        cap.release()
        logger.info(f"Video capture released. Extracted {len(frames)} frames")

    logger.info(
        f"Timestamp-based frame extraction completed. Extracted {len(frames)} frames"
    )
    return frames


def generate_frame_urls(
    frame_dir_name: str, frame_filenames: list[str], base_url: Optional[str] = None
) -> list[str]:
    if base_url is None:
        base_url = ""

    logger.info(
        f"Generating URLs for {len(frame_filenames)} frames in directory: {frame_dir_name}"
    )
    urls = [
        f"{base_url}/{FRAMES_ENDPOINT}/{frame_dir_name}/{filename}"
        for filename in frame_filenames
    ]
    logger.debug(f"Generated {len(urls)} frame URLs")
    return urls


def zip_frames(frame_urls: list[str], name: str, removebg: bool = False) -> str:
    logger.info(
        f"Zipping {len(frame_urls)} frames with name: {name}, removebg: {removebg}"
    )

    cache_folder = get_cache_folder()
    frames_dir = os.path.join(cache_folder, FRAMES_ENDPOINT)

    with tempfile.TemporaryDirectory() as temp_dir:
        renamed_files = []

        for i, url in enumerate(frame_urls):
            parts = url.strip("/").split("/")
            if len(parts) < 3 or parts[0] != FRAMES_ENDPOINT:
                logger.warning(f"Invalid frame URL: {url}")
                continue
            frame_dir_name = parts[1]
            filename = parts[2]

            original_path = os.path.join(frames_dir, frame_dir_name, filename)

            if not os.path.exists(original_path):
                logger.warning(f"Frame file not found: {original_path}")
                continue

            if removebg:
                try:
                    processed_filename = f"processed_{filename}"
                    processed_path = remove_solid_background(
                        original_path, processed_filename
                    )
                    source_path = processed_path
                    logger.debug(f"Background removed for frame {i+1}")
                except Exception as e:
                    logger.warning(f"Failed to remove background for {filename}: {e}")
                    source_path = original_path
            else:
                source_path = original_path

            ext = os.path.splitext(filename)[1]
            new_filename = f"{name}_{i:04d}{ext}"
            new_path = os.path.join(temp_dir, new_filename)

            shutil.copy2(source_path, new_path)
            renamed_files.append(new_path)

        if not renamed_files:
            raise HTTPException(status_code=400, detail="No valid frame files found")

        zip_filename = f"{name}_frames.zip"
        zip_path = os.path.join(cache_folder, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in renamed_files:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)

        logger.info(f"Zip file created: {zip_path}")
        return zip_path


def process_split_frames(request: FrameSplitRequest) -> dict:
    logger.info(f"Processing frame split request for task: {request.task_id}")
    logger.info(
        f"Video URL: {request.video_url}, From: {request.from_time}s, To: {request.to_time}s, Count: {request.count}"
    )

    try:
        video_path = get_or_download_file(request.video_url)

        logger.info("Validating video file and extracting properties")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Cannot open video file for processing")
            raise HTTPException(status_code=500, detail="Cannot open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        cap.release()
        logger.info(
            f"Video FPS: {fps}, Duration: {duration}s, Total frames: {total_frames}"
        )

        if fps <= 0:
            logger.error(f"Invalid video FPS: {fps}")
            raise HTTPException(status_code=400, detail="Invalid video FPS")

        if (
            request.from_time < 0
            or request.to_time > duration
            or request.from_time >= request.to_time
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time range. Video duration: {duration}s, requested: {request.from_time}s - {request.to_time}s",
            )

        time_range = request.to_time - request.from_time
        if request.count <= 1:
            timestamps = [request.from_time]
        else:
            interval = time_range / (request.count - 1)
            timestamps = [
                request.from_time + i * interval for i in range(request.count)
            ]

        logger.info(f"Calculated timestamps: {timestamps}")

        cache_folder = get_cache_folder()
        frame_dir_path, frame_dir_name = create_frame_directory(
            request.task_id, cache_folder
        )

        frame_filenames = extract_frames_at_timestamps(
            video_path, timestamps, frame_dir_path
        )

        frame_urls = generate_frame_urls(frame_dir_name, frame_filenames)

        logger.info(
            f"Frame processing completed successfully. Generated {len(frame_urls)} frame URLs"
        )
        return {"frames": frame_urls}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Frame processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Frame processing failed: {str(e)}"
        )
