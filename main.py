import asyncio

from beartype import beartype as typed
from langchain_openai.chat_models import ChatOpenAI  # type: ignore

model = ChatOpenAI(model_name="gpt-3.5-turbo")


@typed
def assert_is_str(prompt) -> str:
    assert isinstance(prompt, str)
    return prompt


@typed
async def batch_invoke(prompts: list[str]) -> list[str]:
    result = await asyncio.gather(*[model.ainvoke(prompt) for prompt in prompts])
    unpacked = [assert_is_str(message.content) for message in result]
    return unpacked


async def main():
    print(*(await batch_invoke(["hello", "bye"])), sep="\n")


if __name__ == "__main__":
    asyncio.run(main())
