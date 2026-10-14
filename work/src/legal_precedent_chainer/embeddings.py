from __future__ import annotations

import hashlib
import json
from typing import Iterable, List

import numpy as np
import requests

from legal_precedent_chainer import config


class AzureEmbeddingClient:
    def __init__(self) -> None:
        self.endpoint = config.AZURE_OPENAI_ENDPOINT.rstrip("/")
        self.api_key = config.AZURE_OPENAI_API_KEY
        self.api_version = config.AZURE_OPENAI_API_VERSION
        self.deployment = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT

    @property
    def enabled(self) -> bool:
        return all([self.endpoint, self.api_key, self.deployment])

    def _url(self) -> str:
        return (
            f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings"
            f"?api-version={self.api_version}"
        )

    def embed_many(self, texts: Iterable[str]) -> List[List[float]]:
        text_list = list(texts)
        if not self.enabled:
            raise RuntimeError("Azure embedding client is not configured.")

        response = requests.post(
            self._url(),
            headers={
                "Content-Type": "application/json",
                "api-key": self.api_key,
            },
            data=json.dumps({"input": text_list}),
            timeout=30,
        )
        response.raise_for_status()

        data = response.json().get("data", [])
        vectors = [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]
        return vectors



def _deterministic_vector(text: str, dim: int) -> List[float]:
    raw = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(raw[:8], "big", signed=False)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim)
    norm = np.linalg.norm(vec)
    if norm == 0.0:
        return vec.tolist()
    return (vec / norm).tolist()


class EmbeddingProvider:
    def __init__(self) -> None:
        self.azure = AzureEmbeddingClient()

    def embed_many(self, texts: Iterable[str]) -> List[List[float]]:
        text_list = list(texts)
        if self.azure.enabled:
            try:
                return self.azure.embed_many(text_list)
            except Exception:
                pass

        return [_deterministic_vector(text, config.EMBEDDING_FALLBACK_DIM) for text in text_list]
