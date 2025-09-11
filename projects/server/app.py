from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from fastapi.routing import APIRoute
from services.path import get_log_folder, get_cache_folder
from routers.generation_router import router as generation_router


def setup_logging():
    logs_dir = get_log_folder()
    os.makedirs(logs_dir, exist_ok=True)

    log_file_pattern = os.path.join(logs_dir, "pixelda_server.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = TimedRotatingFileHandler(
        log_file_pattern, when="midnight", interval=1, backupCount=30
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    current_log_file = file_handler.baseFilename
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging initialized. Daily log rotation enabled. Current log file: {os.path.basename(current_log_file)}"
    )

    return current_log_file


log_file = setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="PiXelDa Server",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frames_dir = os.path.join(get_cache_folder(), "frames")
os.makedirs(frames_dir, exist_ok=True)

app.include_router(generation_router)

app.mount("/frames", StaticFiles(directory=frames_dir), name="frames")

logger.info("Active endpoints:")
for route in app.routes:
    if isinstance(route, APIRoute):
        logger.info(f"{list(route.methods)} {route.path}")


@app.get("/")
async def root():
    return {"message": "PixelDA Server", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
