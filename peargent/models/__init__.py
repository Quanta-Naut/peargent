from typing import Optional
from peargent.models.gemini import GeminiModel
from peargent.models.groq import GroqModel
from peargent.models.openai import OpenAIModel

def openai(model: str, parameters: dict = None, api_key: Optional[str] = None, endpoint_url: Optional[str] = None):
    return OpenAIModel(model_name=model, parameters=parameters, api_key=api_key, endpoint_url=endpoint_url)

def groq(model: str, parameters: dict = None, api_key: Optional[str] = None, endpoint_url: Optional[str] = None):
    return GroqModel(model_name=model, parameters=parameters, api_key=api_key, endpoint_url=endpoint_url)

def gemini(model: str, parameters: dict = None, api_key: Optional[str] = None, endpoint_url: Optional[str] = None):
    return GeminiModel(model_name=model, parameters=parameters, api_key=api_key, endpoint_url=endpoint_url)