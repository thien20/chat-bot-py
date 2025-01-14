# app/dependencies.py
from aiplatform import AIPlatform

from huggingface_hub import InferenceClient

from .config import config

def get_EN_client():
    return InferenceClient(api_key=config.HF_API_KEY)

def get_VN_client():
    return AIPlatform(api_key=config.KILM_API_KEY)