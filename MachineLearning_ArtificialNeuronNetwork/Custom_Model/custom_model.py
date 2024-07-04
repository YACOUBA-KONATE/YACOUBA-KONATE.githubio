from typing import Optional
from dspy import LM

import openai
import os


class CustomLM(LM):
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        api_url: str = "https://llm-proxy.sandbox.indeed.net/openai/v1/",
        **kwargs
    ):
        self.api_key = api_key if api_key else os.environ.get("OPENAI_API_KEY")
        self.organization = (
            organization if organization else os.environ.get("OPENAI_ORGANIZATION")
        )
        self.base_url = api_url
        self.headers = {"x-indeed-redact-allow": "*"}
        self.client = openai.OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.base_url,
            default_headers=self.headers,
        )
        self.provider = "default"

        self.history = []

        self.kwargs = {
            "temperature": 0.0,
            "max_tokens": 150,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "model": "gpt-3.5-turbo",
            "n": 1,
            **kwargs,
        }

    def basic_request(self, prompt: str, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(messages=messages, **kwargs)

        self.history.append(
            {
                "prompt": prompt,
                "response": {
                    "choices": [
                        {"text": result.message.content} for result in response.choices
                    ]
                },
                "kwargs": kwargs,
            }
        )
        return response

    def __call__(self, prompt, only_completed=True, return_sorted=False, **kwargs):
        response = self.request(prompt, **kwargs)
        completions = [result.message.content for result in response.choices]

        return completions


if __name__ == "__main__":
    custom_lm = CustomLM()

    print("\n\n", custom_lm("Hello", **{"model": "gpt-3.5-turbo"}))
