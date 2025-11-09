# peargent/models/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseModel(ABC):
    """
    All model implementations should inherit from this interface.
    """

    def __init__(self, model_name: str, parameters: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.parameters = parameters or {}

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text completion from the prompt."""
        pass

    async def agenerate(self, prompt: str) -> str:
        """Async version of the generate method."""
        from asyncio import to_thread
        return await to_thread(self.generate, prompt)
