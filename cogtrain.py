import argparse
import asyncio
import json
import random
import time

from beartype import beartype as typed
from gpt import assert_is_str
from tasks import task_info

"""
A command-line tool for creativity training. 

## Supported tasks

Creativity:

1. Insight (IS): An unusual sitiation is described and the participant is asked to think of different causes for the situation.
2. Utopian situations  (US): The participant is instructed to imagine himself in a utopian situation and identify original consequences.
3. Product improvement (PI): The participant is prompted to think about how to improve a product, e.g. toy elephant, to make it more popular and interesting.
4. Alternative uses (AU): Generating novel uses for common objects.
5. Remote associates (RA): The participant is presented with three seemingly unrelated words and must find a fourth word that connects them all. This task measures associative thinking and the ability to make novel connections.

## Architecture

- `batch_invoke(prompts: list[str]): list[str]`. The main interface to call chat assistants.
- `append_jsonl(path: str, data: JSON): None`. Appends json line to a jsonl file.
- `read_jsonl(path: str): list[JSON]`. Reads json lines from a given file.
- `task_info: dict[tuple[Callable[[], list[str]], Callable[[str, list[str]], dict]]]`. Dictionary that for a task name a function to generate tasks of this type, and a function that takes task and responses and returns metrics.
- `prepare_tasks(task_name: str, samples: int): None`. Generates instances of a given task type and stores them to `f"data/{task_name}_{samples}.jsonl"`.
- `test_on_task(task_name: str, samples: int, timeout: int): None`. Gives `samples` instances of a given task type to the participant, taking his responses that were given during `timeout` seconds, grading them, and storing metrics in `f"data/{task_name}_{results}.jsonl"`.
- `show_results(task_name: str, metric: str): None`. Shows the results of a given task type and metric as a Matplotlib plot.
- Command-line interface based on `argparse` which recognizes `prepare TASK_NAME --n SAMPLES`, `test TASK_NAME --n SAMPLES --t TIMEOUT` and `show TASK_NAME --m METRIC` commands.
"""


JSON = dict | list | str


@typed
def append_jsonl(path: str, samples: list[JSON]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        for sample in samples:
            json_string = json.dumps(sample, ensure_ascii=False)
            print(json_string, file=f, flush=True)


@typed
def read_jsonl(path: str) -> list[JSON]:
    result: list[JSON] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            result.append(json.loads(line))
    return result


@typed
def prepare_tasks(task_name: str, samples: int) -> None:
    buffer: list[str] = []
    prepare_fn, grade_fn = task_info[task_name]
    while len(buffer) < samples:
        buffer.extend(prepare_fn())
        print(f"Prepared {len(buffer)} samples...")
    append_jsonl(f"data/{task_name}_samples.jsonl", buffer)


@typed
def test_on_task(task_name: str, samples: int, timeout: int) -> None:
    tasks = read_jsonl(f"data/{task_name}_samples.jsonl")
    selected = random.sample([assert_is_str(x) for x in tasks], samples)
    generate_fn, grade_fn = task_info[task_name]

    extra_questions = [
        assert_is_str(q) for q in read_jsonl("data/extra_questions.jsonl")
    ]
    extra_answers = {}
    for q in extra_questions:
        extra_answers[q] = input(f"{q}\n")
    print()

    for task in selected:
        input(f"\n\n{task_name} task. Press Enter when ready.\n\n")
        print(task)
        t_start = time.time()
        responses = []
        while True:
            remaining = timeout - (time.time() - t_start)
            if remaining < 0:
                break
            response = input(f"{int(remaining)} seconds remaining: ")
            remaining = timeout - (time.time() - t_start)
            if remaining < 0:
                print("Timeout")
                break
            responses.append(response)
        metrics = grade_fn(task, responses)
        metrics["unix_time"] = int(time.time())
        metrics.update(extra_answers)
        append_jsonl(f"data/{task_name}_results.jsonl", metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        type=str,
        choices=["prepare", "test", "show"],
    )
    parser.add_argument(
        "task_name",
        type=str,
        choices=task_info.keys(),
    )
    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Number of samples to prepare or to use in testing",
    )
    parser.add_argument(
        "--t",
        type=int,
        default=120,
        help="Timeout in seconds for each test task",
    )
    parser.add_argument(
        "--m",
        type=str,
        help="Metric to show results for",
    )
    args = parser.parse_args()

    if args.action == "prepare":
        prepare_tasks(args.task_name, args.n)
    elif args.action == "test":
        test_on_task(args.task_name, args.n, args.t)
    elif args.action == "show":
        print("Not implemented yet")
