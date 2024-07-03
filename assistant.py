from typing import Iterable
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import env
from pprint import pprint

import http.client

class Assistant:
    def __init__(self, temperature = 0.1, model = "meta-llama/Meta-Llama-3-8B-Instruct", system_prompt = "", local = False, messages = []) -> None:
        self.temperature = temperature
        self.model = model
        self.description = system_prompt
        self.top_p = 1
        if local:
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )
        else:
            self.client = OpenAI(
                api_key=env.api_key,
                base_url=env.base_url,
            )

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

        res: Stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages, # type: ignore
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=8192,
            stream=True
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

        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages, # type: ignore
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=8192,
            stream=False
        )

        response = res.choices[0].message.content

        self.messages.append({
            "role": "assistant",
            "content": response
        })

        return response or ""

    def get_messages(self):
        return self.messages
