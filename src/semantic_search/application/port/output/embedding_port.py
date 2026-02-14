from abc import ABC, abstractmethod
from typing import List


class EmbeddingPort(ABC):
    """임베딩 생성 인터페이스"""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        텍스트를 임베딩 벡터로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (384차원)
        """
        pass
