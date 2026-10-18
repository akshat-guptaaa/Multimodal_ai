import os
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

def get_secret(name, default=""):
    value = os.getenv(name, "").strip()
    if value:
        return value

    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default

OPENAI_KEY = get_secret("OPENAI_KEY")


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
