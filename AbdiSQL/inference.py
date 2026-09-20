"""
AbdiSQL - Standalone Inference Script
Given a database schema and a natural language question, generates a precise SQLite query.
Supports loading merged weights or 4-bit base model + LoRA adapter.
"""

import argparse
import re

SYSTEM_PROMPT = (
    "You are AbdiSQL, a domain-expert language model specialized in generating "
    "precise SQLite queries from database schemas and questions."
)


def extract_sql(raw_text: str) -> str:
    """Extracts SQL query from markdown block or raw generation."""
    text = raw_text.strip()
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sql_lines = [l for l in lines if re.match(r"^(SELECT|WITH|INSERT|UPDATE|DELETE)", l, re.I)]
    return "\n".join(sql_lines) if sql_lines else text


def load_model(model_path: str, load_4bit: bool = True):
    """Loads tokenizer and causal LM model (imports torch & transformers lazily)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    print(f"Loading AbdiSQL from: {model_path} (4-bit: {load_4bit})...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if load_4bit and torch.cuda.is_available():
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto" if torch.cuda.is_available() else None,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True
        )
        if device == "cpu":
            model.to("cpu")

    return tokenizer, model


def generate_sql(tokenizer, model, schema: str, question: str, max_new_tokens: int = 128) -> str:
    """Generates SQL query given schema and question."""
    import torch
    user_content = f"{schema}\n\nQuestion: {question}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    device = model.device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    prompt_len = inputs["input_ids"].shape[1]
    raw_gen = tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens=True).strip()
    return extract_sql(raw_gen)


def main():
    parser = argparse.ArgumentParser(description="AbdiSQL CLI Inference")
    parser.add_argument(
        "--model_path",
        type=str,
        default="/content/drive/MyDrive/abdi/abdisql/merged_model",
        help="Path to merged model weights or base model"
    )
    parser.add_argument(
        "--schema",
        type=str,
        required=True,
        help="Database schema description (tables, columns, types)"
    )
    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="Natural language question to translate into SQL"
    )
    parser.add_argument(
        "--no_4bit",
        action="store_true",
        help="Disable 4-bit quantization"
    )
    args = parser.parse_args()

    tokenizer, model = load_model(args.model_path, load_4bit=not args.no_4bit)
    sql_result = generate_sql(tokenizer, model, args.schema, args.question)
    print("\n================ GENERATED SQL ================")
    print(sql_result)
    print("===============================================")


if __name__ == "__main__":
    main()
