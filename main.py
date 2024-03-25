import torch as t
from beartype import beartype as typed
from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
device = "cuda" if t.cuda.is_available() else "cpu"


@typed
def loss_bits(text: str) -> float:
    tokenized = tokenizer(text, return_tensors="pt")
    tokenized_device = {k: v.to(device) for k, v in tokenized.items()}
    return model(**tokenized_device).loss


@typed
def loss_bits_prompt(prompt: str, text: str) -> float:
    return loss_bits(prompt + text) - loss_bits(prompt)
