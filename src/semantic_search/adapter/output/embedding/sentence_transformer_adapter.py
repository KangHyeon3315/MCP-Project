from sentence_transformers import SentenceTransformer
from typing import List, Optional
import logging

from ....application.port.output.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)


class SentenceTransformerAdapter(EmbeddingPort):
    """Sentence Transformers 기반 임베딩 어댑터"""

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self):
        self._model: Optional[SentenceTransformer] = None  # 지연 로딩

    def _load_model(self) -> None:
        """모델 지연 로딩 (첫 사용 시에만 로드)"""
        if self._model is None:
            logger.info(f"Loading sentence-transformers model: {self.MODEL_NAME}")
            self._model = SentenceTransformer(self.MODEL_NAME)
            logger.info("Model loaded successfully")

    def generate_embedding(self, text: str) -> List[float]:
        """
        텍스트를 384차원 벡터로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (384차원)
        """
        self._load_model()

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # 텍스트를 임베딩으로 변환
        embedding = self._model.encode(text, convert_to_numpy=True)

        return embedding.tolist()
