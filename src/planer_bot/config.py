import os
import secrets
from logging import getLogger
from typing import Annotated

import firebase_admin  # type: ignore
import openai
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from firebase_admin import credentials, firestore
from linebot.v3.messaging import (  # type: ignore
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from planer_bot.aio_webhook_handler import AsyncWebhookHandler  # type: ignore

logger = getLogger("uvicorn.app")

# Load the environment variables from the .env file
DOTENV_PATH = os.path.join(os.path.dirname(__file__), "../../.env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV_PATH)

    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    OPENAI_API_KEY: str
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str 

    FIRESTORE_EMULATOR_HOST: str | None = None

settings = Settings() # type: ignore


# Webhook Handler for LINE Messaging API
handler = AsyncWebhookHandler(settings.LINE_CHANNEL_SECRET)
line_bot_api = AsyncMessagingApi(
    AsyncApiClient(Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN))
)


# FireStore Client
if settings.FIRESTORE_EMULATOR_HOST:
    db = firestore.Client()
else:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.Client()


# OpenAI Client
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


# Basic Auth settings
security = HTTPBasic()
def basic_authenticate(
    credentials: HTTPBasicCredentials = Depends(security),
) -> HTTPBasicCredentials:
    correct_username = secrets.compare_digest(credentials.username, settings.BASIC_AUTH_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.BASIC_AUTH_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

BasicAuthDep = Annotated[HTTPBasicCredentials, Depends(basic_authenticate)]

