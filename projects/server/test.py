from services.gen_models.model_wrapper import ModelRouter
from defs import VideoGenerationRequest, ImageGenerationRequest
import os


def test_generation_flow():
    test_prompt = "A high-resolution pixel-art game asset depicting a beautiful woman in a black suit and pink glasses, wearing black shoes, standing in a relaxed pose with arms at sides, full-body front view facing straight ahead, against a green screen background, featuring sharp edges, vibrant colors, and crisp pixel details."

    print("Starting image generation...")
    image_request = ImageGenerationRequest(
        prompt=test_prompt,
        negative_prompt="background gradient, background elements",
        size="1024*1024",
        model_type="tongyi",
    )
    print(f"Using model type: {image_request.model_type}")
    image_url = ModelRouter.generate_image(image_request)

    if image_url is None:
        print("Image generation failed")
        return

    print(f"Image generated: {image_url}")

    video_prompt = "Turn right, and run."
    print("Starting video generation...")
    video_request = VideoGenerationRequest(
        api_key=os.getenv("DASHSCOPE_API_KEY", "your-api-key-here"),
        base_image_url=image_url,
        prompt=video_prompt,
        resolution="480P",
        negative_prompt="background gradient, background elements",
        model_type="tongyi",
    )
    print(f"Using model type: {video_request.model_type}")
    video_url = ModelRouter.generate_video(video_request)

    if video_url is None:
        print("Video generation failed")
        return

    print(f"Video generated: {video_url}")
    print("Test completed successfully!")


if __name__ == "__main__":
    test_generation_flow()
