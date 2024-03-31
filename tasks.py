import asyncio
import json
from random import random
from typing import Callable

import numpy as np
from beartype import beartype as typed
from gpt import batch_invoke, invoke

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
- Command-line interface based on `argparse` which recognizes `prepare TASK_NAME SAMPLES`, `test TASK_NAME SAMPLES TIMEOUT` and `show TASK_NAME METRIC` commands.
"""


Info = tuple[Callable[[], list[str]], Callable[[str, list[str]], dict]]
task_info: dict[str, Info] = {}


@typed
def prepare_IS() -> list[str]:
    prompt = """
Please generate 5 examples of insight tasks that could be used in a psychology study. 
Each example is a description of an unusual situation. In the next stage of the test participants will be asked to think of possible causes of these situations.
Provide the output as a JSON array of strings.

Example output:
[
  "A small village that has always been known for its sunny weather and lack of rainfall suddenly experiences a week of non-stop rain, leading to the streets flooding and the villagers being utterly unprepared.",
  "A high school basketball team, which has been losing every game for the entire season, surprisingly wins against the top team in the league by a significant margin.",
  "In a bustling city, a street performer plays music every day and always draws a large crowd. One day, despite playing the same music at the same time and place, no one stops to listen.",
  "A family of four goes to bed at their usual time, but in the morning, they all wake up in a different room of the house, not remembering how they got there.",
  "In a small, tight-knit community, a rumor about a hidden treasure buried somewhere within the town spreads rapidly, inciting a frenzy of digging and searches by the locals."
]
""".strip()
    task_description = "An unusual situation is described below, your task is to think of different causes for the situation."
    while True:
        try:
            response = invoke(prompt, gpt4=(random() < 0.5))
            if response.startswith("```json"):
                response = response[7:-3]
            results = json.loads(response)
            assert isinstance(results, list)
            prompted = [task_description + "\n" + task for task in results]
            return prompted
        except:
            print(f"Error: {response}")


@typed
def grade_originality(task: str, responses: list[str]) -> dict:
    k = 5
    gradings: list[list[float]] = [[] for _ in responses]

    prompts = []
    for response in responses:
        prompt = f"""
You are evaluating responses of participants in a creativity training study. 
The task given to them was:
{task}

The response is:
{response}

Please grade its originality on a 0 to 10 scale.
That is, 0 means the most common or trivial answer, 10 is a really imaginative one.
Provide your grade as a single integer, don't print anything else.
""".strip()
        prompts.extend([prompt for _ in range(k)])
    gpt_responses = asyncio.run(batch_invoke(prompts))
    for i in range(len(gpt_responses)):
        try:
            parsed = float(gpt_responses[i].strip())
            gradings[i // k].append(parsed)
        except Exception as e:
            print(e)
            print(gpt_responses[i])
    originality_scores = np.array([sum(a) / len(a) for a in gradings])
    return {
        "fluency": len(responses),
        "mean_originality": originality_scores.mean(),
        "total_originality": originality_scores.sum(),
        "originality_scores": originality_scores.tolist(),
    }


task_info["IS"] = (prepare_IS, grade_originality)


@typed
def prepare_US() -> list[str]:
    prompt = """
Please generate 10 examples of weird worlds, which have one major distinction from ours.
Generate only very unique universes, which nobody has thought of before.
Also don't provide too different worlds, they should look similar to ours, except for one local difference.
Provide the output as a JSON array of strings.

Example output:
[
    "A world where all secrets are protected by unbreakable encryption, ensuring privacy and security.",
    "In this reality, the concept of currency does not exist. Instead, all societies operate on a sophisticated barter system, where goods and services are exchanged directly based on mutual agreements.",
    "In a parallel universe, all forms of transportation are based on sophisticated floating technologies. Vehicles, buildings, and even personal movements are powered by anti-gravity devices.",
    "A world where plasma weapons have replaced traditional firearms as the primary means of defense.",
    "Here, plants possess the ability to grow at an accelerated rate, maturing from seedlings to full-grown in just a few days, depending on the species.",
    "In this alternate reality, water behaves as a rare and non-renewable resource due to a unique geological history of the planet.",
    "A world where invisibility cloaks enable individuals to move about undetected.",
    "This parallel world discovered a natural resource that emits a constant, gentle light.",
    "In another universe, the concept of sleep does not exist for any living creature. Instead, beings have evolved to rest and rejuvenate through an hour of complete stillness and silence each day.",
    "Here, the gravitational force of the Earth is half as strong as in our universe.",
]
""".strip()
    task_description = "An utopical situation is described below, your task is to think of interesting consequences from it."
    while True:
        try:
            response = invoke(prompt, gpt4=True, T=1.5)
            if response.startswith("```json"):
                response = response[7:-3]
            results = json.loads(response)
            assert isinstance(results, list)
            prompted = [task_description + "\n" + task for task in results]
            return prompted
        except:
            print(f"Error: {response}")

task_info["US"] = (prepare_US, grade_originality)


@typed
def prepare_PI() -> list[str]:
    prompt = """
Please generate 30 examples of products that might be popular among common people.
Provide the output as a JSON array of strings.

Example output:
[
    "Wireless keyboard",
    "Mechanical pencil",
    "Lava lamp",
    "Trash bags",
    "Reusable water bottle",
    "Electric toothbrush",
    "Laptop backpack",
    "Yoga mat",
    "Comfortable and durable sneakers",
    "Magnifying glass",
    "Bluetooth speakers",
    "Silicone baking mat",
    "Eco-friendly shopping bags",
    "Skincare product",
    "Fitness tracker band",
    "Cotton bed sheet",
    "High-speed HDMI cable",
    "Solar-powered garden light",
    "Memory foam pillow",
    "Reusable silicone food bag",
    "Photo album",
    "Desktop calendar",
    "Biodegradable phone case",
    "Digital kitchen scale",
    "Clip-on book reading light",
    "Desk organizer",
    "Spice rack organizer",
    "Reusable makeup remover pad",
    "Scented candle",
    "MP3 player",
]
""".strip()
    task_description = "For a product given below you need to suggest possible improvements, as many and as original as possible."
    while True:
        try:
            response = invoke(prompt, gpt4=True, T=1.0)
            if response.startswith("```json"):
                response = response[7:-3]
            results = json.loads(response)
            assert isinstance(results, list)
            prompted = [task_description + "\n" + task for task in results]
            return prompted
        except:
            print(f"Error: {response}")


task_info["PI"] = (prepare_PI, grade_originality)


@typed
def prepare_AU() -> list[str]:
    prompt = """
Please generate 30 everyday objects that might have a different application.
Provide the output as a JSON array of strings.

Example output:
[
    "Straws",
    "Sponges",
    "Glass jar",
    "Vinegar",
    "Paper clips",
    "Duct tape",
    "Tea bags",
    "Ruler",
    "Rubber band",
    "Pencil",
]
""".strip()
    task_description = "An everyday object is given below, think of as many possible ways to use it as possible."
    while True:
        try:
            response = invoke(prompt, gpt4=True, T=1.0)
            if response.startswith("```json"):
                response = response[7:-3]
            results = json.loads(response)
            assert isinstance(results, list)
            prompted = [task_description + "\n" + task for task in results]
            return prompted
        except:
            print(f"Error: {response}")

task_info["AU"] = (prepare_AU, grade_originality)

