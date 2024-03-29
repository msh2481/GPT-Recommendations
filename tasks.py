import asyncio
import json
from typing import Callable

from beartype import beartype as typed

from langchain_openai.chat_models import ChatOpenAI  # type: ignore

model = ChatOpenAI(model_name="gpt-3.5-turbo")


"""
A command-line tool for creativity training. 

## Supported tasks

Creativity:

1. Insight task (IT): An unusual sitiation is described and the participant is asked to think of different causes for the situation.
2. Utopian situations task (UST): The participant is instructed to imagine himself in a utopian situation and identify original consequences.
3. Product improvement task (PIT): The participant is prompted to think about how to improve a product, e.g. toy elephant, to make it more popular and interesting.
4. Alternative Uses Task (AUT): Generating novel uses for common objects.
5. Remote Associates Task (RAT): The participant is presented with three seemingly unrelated words and must find a fourth word that connects them all. This task measures associative thinking and the ability to make novel connections.

## Architecture

- `batch_invoke(prompts: list[str]): list[str]`. The main interface to call chat assistants.
- `append_jsonl(path: str, data: JSON): None`. Appends json line to a jsonl file.
- `read_jsonl(path: str): list[JSON]`. Reads json lines from a given file.
- `task_info: dict[tuple[Callable[[], list[str]], Callable[[str, list[str]], dict]]]`. Dictionary that for a task name a function to generate tasks of this type, and a function that takes task and responses and returns metrics.
- `prepare_tasks(task_name: str, samples: int): None`. Generates instances of a given task type and stores them to `f"data/{task_name}_{samples}.jsonl"`.
- `test_on_task(task_name: str, samples: int, timeout: int): None`. Gives `samples` instances of a given task type to the participant, taking his responses that were given during `timeout` seconds, grading them, and storing metrics in `f"data/{task_name}_{results}.jsonl"`.
- `show_results(task_name: str, metric: str): None`. Shows the results of a given task type and metric as a Matplotlib plot.
- Command-line interface based on `argparse` which recognizes `prepare TASK_NAME SAMPLES`, `test TASK_NAME SAMPLES TIMEOUT` and `show TASK_NAME METRIC` commands.
"""


@typed
def assert_is_str(prompt) -> str:
    assert isinstance(prompt, str)
    return prompt


@typed
def invoke(prompt: str) -> str:
    return assert_is_str(model.invoke(prompt).content)


@typed
async def batch_invoke(prompts: list[str]) -> list[str]:
    result = await asyncio.gather(*[model.ainvoke(prompt) for prompt in prompts])
    unpacked = [assert_is_str(message.content) for message in result]
    return unpacked


Info = tuple[Callable[[], list[str]], Callable[[str, list[str]], dict]]
task_info: dict[str, Info] = {}


@typed
def prepare_IT() -> list[str]:
    return []
