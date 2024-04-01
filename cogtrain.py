import argparse
import asyncio
import json
import random
import time

from beartype import beartype as typed
from gpt import assert_is_str
from tasks import task_info

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
    selected = random.sample(tasks, samples)
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
