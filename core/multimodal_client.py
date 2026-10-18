from openai import OpenAI


class MultimodalClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API Key is missing.")

        self.client = OpenAI(
            base_url="https://api.apinex.bond/v1",
            api_key=api_key,
            timeout=60,  
        )

    def stream_response(self, model_id: str, messages: list, temperature: float):
        stream = self.client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:  
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta