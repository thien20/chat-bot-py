# app/dependencies.py
from aiplatform import AIPlatform

from huggingface_hub import InferenceClient

from .config import HF_API_KEY, KILM_API_KEY

def get_EN_client():
    return InferenceClient(api_key=HF_API_KEY)

def get_VN_client():
    return AIPlatform(api_key=KILM_API_KEY)