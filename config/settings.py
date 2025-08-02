from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def configure_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )