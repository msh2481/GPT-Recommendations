import asyncio
import os

from beartype import beartype as typed

from langchain_openai.chat_models import ChatOpenAI  # type: ignore

assert not os.environ["OPENAI_API_KEY"].endswith("63")


@typed
def assert_is_str(prompt) -> str:
    assert isinstance(prompt, str)
    return prompt


@typed
def invoke(prompt: str, T: float = 1.0, gpt4: bool = False) -> str:
    model = ChatOpenAI(model_name=["gpt-3.5-turbo-0125", "gpt-4-0125-preview"][gpt4], temperature=T)
    return assert_is_str(model.invoke(prompt).content)


@typed
async def batch_invoke(prompts: list[str], T: float = 1.0, gpt4: bool = False) -> list[str]:
    model = ChatOpenAI(model_name=["gpt-3.5-turbo", "gpt-4-turbo-preview"][gpt4], temperature=T)
    result = await asyncio.gather(*[model.ainvoke(prompt) for prompt in prompts])
    unpacked = [assert_is_str(message.content) for message in result]
    return unpacked
