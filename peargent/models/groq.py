#peargent/models/groq.py

import os
import requests
from typing import Optional, Dict
from .base import BaseModel

class GroqModel(BaseModel):
    ENDPOINT_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        parameters: Optional[Dict] = None,
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        super().__init__(model_name, parameters)
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Groq API key not found. Set GROQ_API_KEY in environment or pass `api_key=`.")
        
        self.endpoint_url = endpoint_url or self.ENDPOINT_URL

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.parameters.get("system_prompt", "")},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.parameters.get("temperature", 0.7),
            "max_tokens": self.parameters.get("max_tokens", 8192),
            "tool_choice": "none"
        }
        
        response = requests.post(self.ENDPOINT_URL, headers=headers, json=body)
        
        if response.status_code != 200:
            raise RuntimeError(f"Groq API error: {response.status_code}, {response.text}")
            # return f"Groq API error: {response.status_code}, {response.text}"
        
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")