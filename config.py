from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_SSL = os.getenv("REDIS_SSL")
    OPENAI_API_KEY = os.getenv("OPENAI_CHATGPT")
    MODEL = os.getenv("MODEL")

settings = Settings()