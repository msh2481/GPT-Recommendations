import argparse
import json
import random
import time
from beartype.typing import Sequence

from beartype import beartype as typed

from gpt import assert_is_str
from tasks import TaskInstance, task_info

JSON = dict | list | str

@typed
def clear_jsonl(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        pass

@typed
def append_jsonl(path: str, samples: Sequence[JSON]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        for sample in samples:
            json_string = json.dumps(sample, ensure_ascii=False)
            print(json_string, file=f, flush=True)


@typed
def read_jsonl(path: str) -> Sequence[JSON]:
    result: list[JSON] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            result.append(json.loads(line))
    return result



@typed
def set_used_count(task_name: str, count: int) -> None:
    with open(f"data/{task_name}_used.txt", "w", encoding="utf-8") as f:
        print(count, file=f)


@typed
def get_used_count(task_name: str) -> int:
    try:
        with open(f"data/{task_name}_used.txt", "r", encoding="utf-8") as f:
            return int(f.read())
    except FileNotFoundError:
        set_used_count(task_name, 0)
        return 0

@typed
def shuffle_tasks(task_name: str) -> None:
    used_count = get_used_count(task_name)
    tasks: list[JSON] = list(read_jsonl(f"data/{task_name}_samples.jsonl"))[used_count:]
    random.shuffle(tasks)
    clear_jsonl(f"data/{task_name}_samples.jsonl")
    append_jsonl(f"data/{task_name}_samples.jsonl", tasks)
    set_used_count(task_name, 0)

@typed
def prepare_tasks(task_name: str, samples: int) -> None:
    buffer: list[JSON] = []
    prepare_fn, grade_fn = task_info[task_name]
    while len(buffer) < samples:
        buffer.extend(prepare_fn())
        print(f"Prepared {len(buffer)} samples...")
    append_jsonl(f"data/{task_name}_samples.jsonl", buffer)

@typed
def get_prepared_count(task_name: str) -> int:
    try:
        return len(read_jsonl(f"data/{task_name}_samples.jsonl"))
    except FileNotFoundError:
        return 0

@typed
def prepare_all_tasks(samples: int) -> None:
    counts = {
        task_name: get_prepared_count(task_name)
        for task_name in task_info.keys()
    }
    while True:
        effective = False
        for task_name in task_info.keys():
            if counts[task_name] < samples:
                effective = True
                prepare_tasks(task_name, 100)
                counts[task_name] = get_prepared_count(task_name)
        if not effective:
            break
    for task_name in task_info.keys():
        shuffle_tasks(task_name)


@typed
def test_on_task(task_name: str, samples: int, timeout: int) -> None:
    tasks: list[TaskInstance] = read_jsonl(f"data/{task_name}_samples.jsonl")  # type: ignore
    used_count = get_used_count(task_name)
    selected = tasks[used_count : used_count + samples]
    set_used_count(task_name, used_count + samples)
    generate_fn, grade_fn = task_info[task_name]

    extra_questions = [
        assert_is_str(q) for q in read_jsonl("data/extra_questions.jsonl")
    ]
    extra_answers: dict[str, str] = {}
    for q in extra_questions:
        extra_answers[q] = input(f"{q}\n")
    print()

    for task in selected:
        input(f"\n\n{task_name} task. Press Enter when ready.\n\n")
        print(task["prompt"])
        t_start = time.time()
        responses = []
        time_spent = float(timeout)
        while True:
            current_time_spent = time.time() - t_start
            remaining = timeout - current_time_spent
            if remaining < 0:
                break
            response = input(f"{int(remaining)} seconds remaining: ").strip()
            remaining = timeout - (time.time() - t_start)
            if remaining < 0 or response == "next":
                time_spent = min(timeout, current_time_spent)
                print("Timeout")
                break
            if len(response):
                responses.append(response)
        metrics = grade_fn(task, responses)
        metrics["unix_time"] = int(time.time())
        metrics["prompt"] = task["prompt"]
        if "answer" in task:
            metrics["answer"] = task["answer"]
        metrics["responses"] = responses
        metrics["timeout"] = timeout
        metrics["time_spent"] = time_spent
        metrics.update(extra_answers)
        append_jsonl(f"data/{task_name}_results.jsonl", [metrics])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        type=str,
        choices=["prepare", "test", "shuffle", "show"],
    )
    parser.add_argument(
        "task_name",
        type=str,
        choices=list(task_info.keys()) + ["all"],
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
        if args.task_name == "all":
            prepare_all_tasks(args.n)
        else:
            prepare_tasks(args.task_name, args.n)
    elif args.action == "prepare_all":
        prepare_all_tasks(args.n)
    elif args.action == "test":
        test_on_task(args.task_name, args.n, args.t)
    elif args.action == "shuffle":
        shuffle_tasks(args.task_name)
    elif args.action == "show":
        print("Not implemented yet")
