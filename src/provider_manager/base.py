from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional


class Provider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError()

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def stream(self, prompt: str, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def embeddings(self, texts: Iterable[str], **kwargs) -> List[float]:
        raise NotImplementedError()

    @abstractmethod
    def tool_calls(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        raise NotImplementedError()
