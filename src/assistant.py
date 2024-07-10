from typing import Iterable
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import env
from pprint import pprint
import httpx
import json

import http.client

class Assistant:
    def __init__(self, temperature = 0.1, model = "meta-llama/Meta-Llama-3-8B-Instruct", system_prompt = "", local = False, messages = []) -> None:
        self.temperature = temperature
        self.model = model
        self.description = system_prompt
        self.top_p = 1
        if local:
            self.api_key = "http://localhost:11434/v1"
            self.base_url = "ollama"
        else:
            self.api_key = env.api_key
            self.base_url = env.base_url

        self.messages = messages

    def run_stream(self, question: str) -> Iterable[str]:
        self.messages.append({
            "role": "user",
            "content": question
        })

        messages = [
            {
                "role": "system",
                "content": self.description
            },
            *self.messages
        ]

        res = httpx.post(
            self.base_url + "/chat/completions",
            headers={"Authorization": "bearer " + self.api_key, "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True,
                "max_tokens": 8192
            }
        )

        response = ""
        for chunk in res:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

        self.messages.append({
            "role": "assistant",
            "content": response
        })

    def run(self, question: str) -> str:
        self.messages.append({
            "role": "user",
            "content": question
        })

        messages = [
            {
                "role": "system",
                "content": self.description
            },
            *self.messages
        ]

        res = httpx.post(
            self.base_url + "/chat/completions",
            headers={"Authorization": "bearer " + self.api_key, "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": None
            },
            timeout = 60
        )

        response = res.json()["choices"][0]["message"]["content"]

        self.messages.append({
            "role": "assistant",
            "content": response
        })

        return response or ""

    def get_messages(self):
        return self.messages

    def clear_messages(self):
        self.messages = []
