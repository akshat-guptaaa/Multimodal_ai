import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY", "")

AVAILABLE_MODELS = {
    "GPT6 Luna": {
        "id": "free/gpt-6-luna",
        "supports_vision": True
    },
    "DeepSeek V4 Pro": {
        "id": "free/deepseek-v4-pro-0813",
        "supports_vision": True,
    },
    "MIMO V2.6 Pro": {
        "id": "free/mimo-v2.6-pro",
        "supports_vision": False,
    },
}

MAX_IMAGES_PER_MESSAGE = 4
MAX_HISTORY_MESSAGES = 20
DEFAULT_IMAGE_PROMPT = "Analyze this image and explain what you see."