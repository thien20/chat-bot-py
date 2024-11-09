import os
from dotenv import load_dotenv

load_dotenv()


HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
KILM_API_KEY = os.getenv("AI_PLATFORM_ACCESS_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10