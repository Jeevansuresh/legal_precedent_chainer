from __future__ import annotations

import json
from typing import Any, Dict

import requests

from legal_precedent_chainer import config


class AzureNarrationClient:
    def __init__(self) -> None:
        self.endpoint = config.AZURE_OPENAI_ENDPOINT.rstrip("/")
        self.responses_url = config.AZURE_OPENAI_RESPONSES_URL.rstrip("/")
        self.api_key = config.AZURE_OPENAI_API_KEY
        self.api_version = config.AZURE_OPENAI_API_VERSION
        self.deployment = config.AZURE_OPENAI_CHAT_DEPLOYMENT

    @property
    def enabled(self) -> bool:
        has_responses_mode = all([self.responses_url, self.api_key, self.deployment])
        has_chat_mode = all([self.endpoint, self.api_key, self.deployment])
        return has_responses_mode or has_chat_mode

    def _chat_url(self) -> str:
        return (
            f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
            f"?api-version={self.api_version}"
        )

    def _responses_url(self) -> str:
        return self.responses_url

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
        }

    @staticmethod
    def _extract_json_object(raw_text: str) -> Dict[str, str]:
        parsed = json.loads(raw_text)
        allowed = {"issue", "rule", "application", "conclusion", "suggested_paragraph", "petitioner_paragraph", "respondent_paragraph"}
        return {k: str(v) for k, v in parsed.items() if k in allowed}

    @staticmethod
    def _extract_responses_text(payload: Dict[str, Any]) -> str:
        if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
            return payload["output_text"]

        output = payload.get("output", [])
        if isinstance(output, list):
            for item in output:
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"} and content.get("text"):
                        return str(content["text"])

        raise ValueError("No textual output found in Azure Responses payload")

    def _rewrite_via_responses_api(self, prompt: str, user_payload: Dict[str, str]) -> Dict[str, str]:
        body = {
            "model": self.deployment,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": json.dumps(user_payload)}],
                },
            ],
            "temperature": 0.2,
        }

        response = requests.post(
            self._responses_url(),
            headers=self._headers(),
            data=json.dumps(body),
            timeout=30,
        )
        response.raise_for_status()
        text = self._extract_responses_text(response.json())
        return self._extract_json_object(text)

    def _rewrite_via_chat_completions(self, prompt: str, user_payload: Dict[str, str]) -> Dict[str, str]:
        body = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        response = requests.post(
            self._chat_url(),
            headers=self._headers(),
            data=json.dumps(body),
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._extract_json_object(content)

    def rewrite_brief(self, brief: Dict[str, str], context: Dict[str, str]) -> Dict[str, str]:
        if not self.enabled:
            raise RuntimeError("Azure narration client is not configured")

        prompt = (
            "Rewrite this legal research brief for a practicing lawyer. "
            "Keep it practical, defensible, and aligned to the requested draft length. "
            "Do not add any new case names beyond provided context. "
            "Return strict JSON with keys: issue, rule, application, conclusion, suggested_paragraph, "
            "petitioner_paragraph, respondent_paragraph."
        )

        user_payload = {
            "brief": brief,
            "context": context,
        }

        if self.responses_url:
            return self._rewrite_via_responses_api(prompt, user_payload)

        return self._rewrite_via_chat_completions(prompt, user_payload)
