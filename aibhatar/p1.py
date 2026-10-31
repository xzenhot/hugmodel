import random
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Output goes next to this script unless a path is passed as argv[1]
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "bengali_sonnet.txt"
OUTPUT_FILE = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT

# 1. Load Model: 4-bit on GPU, bf16 on CPU
model_id = "ai4bharat/IndicBERT-v3-4B"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

if torch.cuda.is_available():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.bfloat16,
        trust_remote_code=True
    )
model.eval()

MASK_ID = tokenizer.mask_token_id


def sample_masked_line(fixed_end_token_str, line_token_length=10, steps=25):
    """
    Fills a line of length `line_token_length` ending in `fixed_end_token_str`
    using iterative Gibbs sampling via IndicBERT-v3 MNTP.
    """
    end_ids = tokenizer.encode(fixed_end_token_str, add_special_tokens=False)
    end_token_id = end_ids[-1]

    # Initialize line: [BOS] + [MASK]*N + EndToken + [EOS]
    line_ids = [tokenizer.bos_token_id] + [MASK_ID] * (line_token_length - 2) + [end_token_id, tokenizer.eos_token_id]
    device = next(model.parameters()).device
    input_ids = torch.tensor([line_ids], device=device)

    mask_positions = list(range(1, line_token_length - 1))

    with torch.no_grad():
        for step in range(steps):
            # Simulated annealing temperature
            temp = max(0.4, 1.2 * (1.0 - (step / steps)))

            # Pick one position to resample
            idx = random.choice(mask_positions)
            input_ids[0, idx] = MASK_ID

            outputs = model(input_ids)
            # IndicBERT-v3 MNTP: token at 'idx' is predicted by logits at (idx - 1)
            pred_logits = outputs.logits[0, idx - 1, :].float().clone()

            # Suppress special tokens
            pred_logits[tokenizer.all_special_ids] = -float("inf")

            probs = torch.softmax(pred_logits / temp, dim=-1)
            sampled_id = torch.multinomial(probs, num_samples=1).item()

            input_ids[0, idx] = sampled_id

    generated_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    return generated_text.strip()


# 2. Sonnet Orchestration
# Define 14 end-rhymes matching an ABAB CDCD EFEF GG scheme
rhyme_anchors = [
    "রাতে", "আলো", "সাথে", "ভালো",       # Quatrain 1: A B A B
    "ভাসে", "দূরে", "আসে", "সুরে",       # Quatrain 2: C D C D
    "মায়ায়", "গান", "ছায়ায়", "প্রাণ",    # Quatrain 3: E F E F
    "মন", "ক্ষণ"                        # Couplet:    G G
]

sonnet_lines = []
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
for anchor in rhyme_anchors:
    line = sample_masked_line(fixed_end_token_str=anchor, line_token_length=10, steps=20)
    sonnet_lines.append(line)
    print(line, flush=True)
    # Flush partial progress so a long run is never lost
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sonnet_lines) + "\n")

stanzas = [sonnet_lines[0:4], sonnet_lines[4:8], sonnet_lines[8:12], sonnet_lines[12:14]]
sonnet = "\n\n".join("\n".join(stanza) for stanza in stanzas)

print("\n--- Generated Sonnet ---\n")
print(sonnet)
print()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(sonnet + "\n")
print(f"Sonnet written to {OUTPUT_FILE}")
