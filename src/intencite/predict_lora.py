from copy import deepcopy
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER_PATH = ROOT / "models" / "lora_adapter"

LABELS = [
    "Application",
    "Background",
    "Comparison",
    "Gap",
    "Improvement",
]

SYSTEM_PROMPT = (
    "You classify the function of a citation in a scientific paper. "
    "The target reference is wrapped in <cite> </cite>. "
    "Reply with exactly one of these labels and nothing else:\n"
    "Application - the citing work uses an idea, method or tool from the cited work\n"
    "Background - the reference gives context about the domain or the problem\n"
    "Comparison - the citing work points out similarities or differences with the cited work\n"
    "Gap - the reference motivates the work by pointing to an unmet need\n"
    "Improvement - the citing work extends or modifies an idea or method from the cited work"
)

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model

    if _model is not None:
        return

    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=(torch.float16 if _device.type == "cuda" else torch.float32),
    )

    _model = PeftModel.from_pretrained(
        base_model,
        ADAPTER_PATH,
    )

    _model.to(_device)
    _model.eval()

    if hasattr(_model, "config"):
        _model.config.use_cache = True


def _to_messages(context: str):
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": context,
        },
    ]


@torch.inference_mode()
def predict_lora(context: str) -> dict:
    _load_model()

    messages = _to_messages(context)

    # ---------------------------------------------------------
    # 1. Build the shared prompt.
    # ---------------------------------------------------------

    prompt_ids = _tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=False,
    ).to(_device)

    prompt_length = prompt_ids.shape[1]

    # ---------------------------------------------------------
    # 2. Process the shared prompt only once.
    #
    #    The KV cache contains the transformer state produced
    #    by the system prompt + citation context.
    # ---------------------------------------------------------

    prompt_output = _model(
        input_ids=prompt_ids,
        use_cache=True,
    )

    # The logits at the last prompt position predict
    # the first token of the assistant response.
    first_token_logprobs = torch.log_softmax(
        prompt_output.logits[0, -1].float(),
        dim=-1,
    )

    prompt_cache = prompt_output.past_key_values

    # Logits from the full prompt are no longer required.
    del prompt_output

    scores = []

    # ---------------------------------------------------------
    # 3. Score each candidate label.
    #
    #    We reuse the prompt KV cache instead of evaluating
    #    the complete prompt five separate times.
    # ---------------------------------------------------------

    for label in LABELS:
        full_messages = messages + [
            {
                "role": "assistant",
                "content": label,
            }
        ]

        full_ids = _tokenizer.apply_chat_template(
            full_messages,
            return_tensors="pt",
            return_dict=False,
        )[0].to(_device)

        # These are exactly the assistant tokens that were
        # scored in the original experiment.
        target = full_ids[prompt_length:]

        # First assistant token is predicted directly from
        # the already processed prompt.
        first_lp = first_token_logprobs[target[0]].unsqueeze(0)

        token_logprobs = [first_lp]

        # -----------------------------------------------------
        # 4. Score remaining assistant tokens.
        #
        #    Usually this includes the rest of the label,
        #    chat-template termination tokens, etc.
        # -----------------------------------------------------

        if target.numel() > 1:
            # Each candidate must start from the exact same
            # prompt state, therefore we clone the cache.
            candidate_cache = deepcopy(prompt_cache)

            # Feed every target token except the final one.
            # Their logits predict target[1:].
            continuation_input = target[:-1].unsqueeze(0)

            attention_mask = torch.ones(
                (
                    1,
                    prompt_length + continuation_input.shape[1],
                ),
                dtype=torch.long,
                device=_device,
            )

            continuation_output = _model(
                input_ids=continuation_input,
                attention_mask=attention_mask,
                past_key_values=candidate_cache,
                use_cache=False,
            )

            continuation_logprobs = torch.log_softmax(
                continuation_output.logits[0].float(),
                dim=-1,
            )

            remaining_targets = target[1:]

            remaining_logprobs = continuation_logprobs.gather(
                1,
                remaining_targets.unsqueeze(1),
            ).squeeze(1)

            token_logprobs.append(remaining_logprobs)

        # Same metric used in the notebook:
        # mean log probability of the candidate tokens.
        label_score = torch.cat(token_logprobs).mean().item()

        scores.append(label_score)

    # ---------------------------------------------------------
    # 5. Convert label scores into probabilities.
    # ---------------------------------------------------------

    scores_tensor = torch.tensor(
        scores,
        dtype=torch.float32,
    )

    probabilities = torch.softmax(
        scores_tensor,
        dim=-1,
    ).tolist()

    probability_dict = dict(
        zip(
            LABELS,
            probabilities,
        )
    )

    prediction_index = int(torch.argmax(scores_tensor).item())

    prediction = LABELS[prediction_index]

    return {
        "model": "qwen2.5-1.5b-lora-3ctx",
        "prediction": prediction,
        "confidence": max(probabilities),
        "probabilities": probability_dict,
    }
