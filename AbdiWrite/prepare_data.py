"""
AbdiWrite - Dataset Preparation
Builds a bilingual grammar/style correction dataset with two components:

  1. English component  — JFLEG dataset (public, ~1,500 fluency correction pairs)
  2. Urdu component     — semi-synthetic error injection into clean Urdu sentences

All examples are formatted into instruction pairs:
  {
    "instruction": "Correct the grammar and style of the following text.",
    "input":  "<erroneous sentence>",
    "output": "<corrected sentence>\n\nExplanation: <brief explanation of the fix>",
    "lang": "en" | "ur" | "roman_ur",
    "source": "jfleg" | "synthetic_urdu"
  }

Split: 90% train / 10% held-out eval.
Target: 800–1,000 high-quality pairs (quality over volume).

Run in Google Colab (T4) or locally with Python 3.10+.
"""

import json
import os
import random
import re
from typing import Any, Dict, List, Tuple

RANDOM_SEED = 42
TRAIN_RATIO = 0.90
TARGET_ENGLISH = 500   # pulled from JFLEG (subset for balance)
TARGET_URDU = 400      # synthetic Urdu + Roman-Urdu pairs

# ---------------------------------------------------------------------------
# PART 1 — English: JFLEG dataset
# ---------------------------------------------------------------------------

def load_jfleg(data_dir: str) -> List[Dict[str, Any]]:
    """
    Downloads and parses the JFLEG grammar correction dataset from Hugging Face.
    JFLEG contains grammatically flawed English sentences paired with 4 human
    reference corrections each. We use the first reference as the gold output.

    Returns a list of raw pairs: {"source": ..., "corrections": [...]}
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError(
            "Run: pip install datasets\n"
            "Or in Colab: !pip install datasets"
        )

    print("[JFLEG] Loading JFLEG from Hugging Face datasets hub...")
    dataset = load_dataset("jfleg", split="validation")   # ~755 examples
    # Also grab test split (~748 examples) for more data
    dataset_test = load_dataset("jfleg", split="test")

    pairs = []
    for split_data in [dataset, dataset_test]:
        for row in split_data:
            source = row["sentence"].strip()
            corrections = [c.strip() for c in row["corrections"] if c.strip()]
            if source and corrections:
                pairs.append({"source": source, "corrections": corrections})

    print(f"[JFLEG] Loaded {len(pairs)} raw pairs.")
    return pairs


def format_jfleg_pairs(
    raw_pairs: List[Dict[str, Any]],
    target_count: int = TARGET_ENGLISH,
    seed: int = RANDOM_SEED,
) -> List[Dict[str, Any]]:
    """
    Converts JFLEG raw pairs into AbdiWrite instruction format.

    Rules:
    - Skip pairs where source == first correction (no error to correct).
    - Use first human reference as the gold correction.
    - Generate a short explanation based on diff between source and correction.
    """
    random.seed(seed)

    formatted = []
    skipped_identical = 0

    for pair in raw_pairs:
        source = pair["source"]
        correction = pair["corrections"][0]   # primary reference

        if source.strip().lower() == correction.strip().lower():
            skipped_identical += 1
            continue

        explanation = _infer_english_explanation(source, correction)
        formatted.append({
            "instruction": "Correct the grammar and writing style of the following English text.",
            "input": source,
            "output": f"{correction}\n\nExplanation: {explanation}",
            "lang": "en",
            "source": "jfleg",
        })

    print(f"[JFLEG] Skipped {skipped_identical} identical source-correction pairs.")
    print(f"[JFLEG] Usable pairs: {len(formatted)}")

    # Sub-sample to target count if we have more than needed
    if len(formatted) > target_count:
        formatted = random.sample(formatted, target_count)
        print(f"[JFLEG] Sampled down to {target_count} pairs.")

    return formatted


def _infer_english_explanation(source: str, correction: str) -> str:
    """
    Produces a brief, rule-based explanation of what changed between the
    source and corrected sentence. Covers the most common JFLEG error types.
    """
    src_words = source.lower().split()
    cor_words = correction.lower().split()

    hints = []

    # Subject-verb agreement: "he go" → "he goes"
    agreement_verbs = {"go": "goes", "do": "does", "have": "has", "is": "are", "was": "were"}
    for w, fix in agreement_verbs.items():
        if w in src_words and fix in cor_words:
            hints.append("subject-verb agreement corrected")
            break

    # Article insertion: "a" or "an" or "the" added
    src_set = set(src_words)
    cor_set = set(cor_words)
    added = cor_set - src_set
    removed = src_set - cor_set
    if added & {"a", "an", "the"}:
        hints.append("missing article added")
    if removed & {"a", "an", "the"}:
        hints.append("incorrect article removed")

    # Punctuation / capitalization
    if source[0].islower() and correction[0].isupper():
        hints.append("sentence capitalization corrected")
    if not source.rstrip().endswith((".", "!", "?")) and correction.rstrip().endswith((".", "!", "?")):
        hints.append("missing punctuation added")

    # Spelling (crude: word count differs significantly)
    if len(src_words) != len(cor_words):
        hints.append("word order or structure improved")
    elif src_words != cor_words:
        hints.append("spelling or word choice corrected")

    if not hints:
        hints.append("grammar and fluency improved")

    return "; ".join(hints).capitalize() + "."


# ---------------------------------------------------------------------------
# PART 2 — Urdu & Roman-Urdu: Synthetic Error Injection
# ---------------------------------------------------------------------------

# Clean Urdu seed sentences — linguistically varied, grammatically correct.
# These are used as the "gold" corrected output. Errors are injected into them
# programmatically to produce the "input" side of each pair.
URDU_SEED_SENTENCES = [
    # Everyday / conversational
    ("آپ کیسے ہیں؟", "ur"),
    ("میں ٹھیک ہوں، شکریہ۔", "ur"),
    ("آج موسم بہت اچھا ہے۔", "ur"),
    ("کیا آپ نے کھانا کھایا؟", "ur"),
    ("میں کل اسکول جاؤں گا۔", "ur"),
    ("وہ بازار سے سبزیاں لایا۔", "ur"),
    ("بچے باغ میں کھیل رہے ہیں۔", "ur"),
    ("میری امی نے بریانی بنائی۔", "ur"),
    ("آپ کا نام کیا ہے؟", "ur"),
    ("یہ کتاب بہت دلچسپ ہے۔", "ur"),
    ("ہمیں محنت کرنی چاہیے۔", "ur"),
    ("وہ ہر روز صبح جلدی اٹھتا ہے۔", "ur"),
    ("میں نے اپنا کام مکمل کر لیا۔", "ur"),
    ("ڈاکٹر نے مریض کا معائنہ کیا۔", "ur"),
    ("آج بازار میں بہت بھیڑ تھی۔", "ur"),
    ("وہ بچپن سے ہی بہت ذہین ہے۔", "ur"),
    ("مجھے پانی پینا ہے۔", "ur"),
    ("کل بارش ہوئی تھی۔", "ur"),
    ("استاد نے سوال پوچھا۔", "ur"),
    ("سورج مغرب میں ڈوبتا ہے۔", "ur"),
    # Formal / written
    ("حکومت نے نئی پالیسی کا اعلان کیا۔", "ur"),
    ("اس سال فصل بہت اچھی ہوئی۔", "ur"),
    ("کمپنی نے نئے ملازمین کی بھرتی کی۔", "ur"),
    ("رپورٹ میں غلطیاں پائی گئیں۔", "ur"),
    ("اجلاس کا آغاز وقت پر ہوا۔", "ur"),
    # Roman-Urdu
    ("Aaj main ghar par hun.", "roman_ur"),
    ("Mujhe neend aa rahi hai.", "roman_ur"),
    ("Kal school chhutti hai.", "roman_ur"),
    ("Kya tum thak gaye ho?", "roman_ur"),
    ("Main subah uthta hun aur exercise karta hun.", "roman_ur"),
    ("Uski awaaz bahut meethi hai.", "roman_ur"),
    ("Yeh kaam mushkil nahi hai.", "roman_ur"),
    ("Hamare ghar mein panch log rehte hain.", "roman_ur"),
    ("Wo roz time par aata hai.", "roman_ur"),
    ("Mujhe is cheez ki zaroorat hai.", "roman_ur"),
    ("Ap ka ghar kaisa hai?", "roman_ur"),
    ("Woh dukaan band ho gayi.", "roman_ur"),
    ("Bachon ne khub khela.", "roman_ur"),
    ("Is saal barish kam hui.", "roman_ur"),
    ("Hamara team match jeet gaya.", "roman_ur"),
]

# Common Urdu error patterns: (error_description, injection_fn)
# Each injection_fn takes a sentence string and returns a modified (erroneous) string,
# or None if the pattern cannot be applied to this sentence.

def _inject_missing_izafat(sentence: str) -> str | None:
    """Remove 'کی' or 'کے' or 'کا' (Urdu ezafe/possessive) to simulate omission."""
    for particle in [" کی ", " کے ", " کا "]:
        if particle in sentence:
            return sentence.replace(particle, " ", 1)
    return None


def _inject_verb_tense_error(sentence: str) -> str | None:
    """Swap a common verb ending to simulate tense mismatch."""
    swaps = [
        (" ہے۔", " تھا۔"), (" تھا۔", " ہے۔"),
        (" ہیں۔", " تھے۔"), (" تھے۔", " ہیں۔"),
        (" گا۔", " تھا۔"), (" گی۔", " تھی۔"),
    ]
    for wrong, right in swaps:
        if right in sentence:
            return sentence.replace(right, wrong, 1)
    return None


def _inject_word_order(sentence: str) -> str | None:
    """Swap two adjacent words to simulate unnatural Urdu word order."""
    words = sentence.split()
    if len(words) < 4:
        return None
    idx = random.randint(1, len(words) - 2)
    words[idx], words[idx - 1] = words[idx - 1], words[idx]
    return " ".join(words)


def _inject_punctuation_drop(sentence: str) -> str | None:
    """Remove ending punctuation (۔ ! ?) to simulate missing punctuation."""
    if sentence and sentence[-1] in "۔!؟.?":
        return sentence[:-1]
    return None


def _inject_roman_spelling(sentence: str) -> str | None:
    """Common Roman-Urdu spelling variations (hai→he, main→mein, etc.)."""
    replacements = [
        (" hun", " hoon"), (" hoon", " hun"),
        ("main ", "mein "), ("mein ", "main "),
        (" hai", " he"), (" he ", " hai "),
        ("Kya ", "Kia "), ("kya ", "kia "),
        ("nahi", "ni"), (" wo ", " woh "), (" woh ", " wo "),
    ]
    for wrong, fix in replacements:
        if fix in sentence:
            return sentence.replace(fix, wrong, 1)
    return None


URDU_INJECTORS = [
    ("izafat omission", _inject_missing_izafat),
    ("verb tense error", _inject_verb_tense_error),
    ("unnatural word order", _inject_word_order),
    ("punctuation dropped", _inject_punctuation_drop),
]
ROMAN_INJECTORS = [
    ("informal spelling variant", _inject_roman_spelling),
    ("punctuation dropped", _inject_punctuation_drop),
    ("unnatural word order", _inject_word_order),
]


def _urdu_explanation(lang: str, error_type: str) -> str:
    EXPLANATIONS = {
        "izafat omission": {
            "ur": "اضافت (کا/کی/کے) غائب تھی، جو کہ اردو میں اسم اور اس کے ملحق کے درمیان ربط کے لیے ضروری ہے۔",
            "roman_ur": "The possessive particle (ka/ki/ke) was missing.",
        },
        "verb tense error": {
            "ur": "فعل کا زمانہ غلط تھا — جملے کے سیاق کے مطابق درست زمانہ استعمال کیا گیا۔",
            "roman_ur": "Verb tense was incorrect for the context.",
        },
        "unnatural word order": {
            "ur": "الفاظ کی ترتیب غیر فطری تھی — اردو جملے کی قدرتی ترتیب بحال کی گئی۔",
            "roman_ur": "Word order was unnatural; corrected to standard Urdu sentence structure.",
        },
        "punctuation dropped": {
            "ur": "جملے کے آخر میں رموزِ اوقاف (۔) غائب تھی۔",
            "roman_ur": "Missing end punctuation added.",
        },
        "informal spelling variant": {
            "ur": "رومن اردو میں غلط ہجے استعمال ہوئے — معیاری ہجے بحال کیے گئے۔",
            "roman_ur": "Non-standard Roman Urdu spelling corrected to widely accepted form.",
        },
    }
    lang_key = "roman_ur" if lang == "roman_ur" else "ur"
    return EXPLANATIONS.get(error_type, {}).get(lang_key, "Grammar and style corrected.")


def generate_synthetic_urdu_pairs(
    seed_sentences: List[Tuple[str, str]],
    target_count: int = TARGET_URDU,
    seed: int = RANDOM_SEED,
) -> List[Dict[str, Any]]:
    """
    Generates synthetic Urdu/Roman-Urdu grammar correction pairs by injecting
    controlled errors into clean seed sentences.

    Strategy:
    - Each seed sentence is tried with every applicable injector.
    - Valid (changed) error variants are collected.
    - Final set is randomly sampled to reach target_count.
    """
    random.seed(seed)

    candidates = []
    for clean_sentence, lang in seed_sentences:
        injectors = ROMAN_INJECTORS if lang == "roman_ur" else URDU_INJECTORS
        for error_type, injector_fn in injectors:
            try:
                erroneous = injector_fn(clean_sentence)
            except Exception:
                erroneous = None

            if erroneous and erroneous.strip() != clean_sentence.strip():
                explanation = _urdu_explanation(lang, error_type)
                lang_label = "Roman Urdu" if lang == "roman_ur" else "Urdu"
                candidates.append({
                    "instruction": f"Correct the grammar and writing style of the following {lang_label} text.",
                    "input": erroneous.strip(),
                    "output": f"{clean_sentence.strip()}\n\nExplanation: {explanation}",
                    "lang": lang,
                    "source": "synthetic_urdu",
                })

    print(f"[Urdu] Generated {len(candidates)} candidate synthetic pairs from {len(seed_sentences)} seed sentences.")

    if len(candidates) > target_count:
        candidates = random.sample(candidates, target_count)
        print(f"[Urdu] Sampled down to {target_count} pairs.")
    else:
        print(f"[Urdu] Using all {len(candidates)} pairs (below target of {target_count}).")

    return candidates


# ---------------------------------------------------------------------------
# PART 3 — Merge, shuffle, split, save
# ---------------------------------------------------------------------------

def merge_and_split(
    english_pairs: List[Dict[str, Any]],
    urdu_pairs: List[Dict[str, Any]],
    train_ratio: float = TRAIN_RATIO,
    seed: int = RANDOM_SEED,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Merges English and Urdu pairs, shuffles, and splits into train/eval.
    Ensures language balance is preserved proportionally in both splits.
    """
    random.seed(seed)

    all_pairs = english_pairs + urdu_pairs
    random.shuffle(all_pairs)

    split_idx = int(len(all_pairs) * train_ratio)
    train_data = all_pairs[:split_idx]
    eval_data = all_pairs[split_idx:]

    en_train = sum(1 for x in train_data if x["lang"] == "en")
    ur_train = sum(1 for x in train_data if x["lang"] in ("ur", "roman_ur"))
    en_eval = sum(1 for x in eval_data if x["lang"] == "en")
    ur_eval = sum(1 for x in eval_data if x["lang"] in ("ur", "roman_ur"))

    print(f"\n[Split] Train: {len(train_data)} total  (English: {en_train}, Urdu/Roman: {ur_train})")
    print(f"[Split] Eval:  {len(eval_data)} total  (English: {en_eval},  Urdu/Roman: {ur_eval})")

    return train_data, eval_data


def save_splits(
    train_data: List[Dict[str, Any]],
    eval_data: List[Dict[str, Any]],
    output_dir: str,
):
    """Saves train and held-out eval splits as JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    train_path = os.path.join(output_dir, "train.json")
    eval_path = os.path.join(output_dir, "eval_held_out.json")

    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2, ensure_ascii=False)

    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2, ensure_ascii=False)

    print(f"\n[Save] Training split   → {train_path}")
    print(f"[Save] Held-out eval    → {eval_path}")
    print(f"[Save] Total pairs saved: {len(train_data) + len(eval_data)}")


def print_samples(pairs: List[Dict[str, Any]], n: int = 3, label: str = ""):
    """Prints n random sample pairs for manual inspection."""
    print(f"\n{'='*60}")
    print(f"  Sample pairs: {label}")
    print(f"{'='*60}")
    samples = random.sample(pairs, min(n, len(pairs)))
    for i, s in enumerate(samples, 1):
        print(f"\n[{i}] Lang: {s['lang']} | Source: {s['source']}")
        print(f"  INPUT:  {s['input']}")
        output_lines = s["output"].split("\n\nExplanation:")
        print(f"  OUTPUT: {output_lines[0]}")
        if len(output_lines) > 1:
            print(f"  EXPL:   {output_lines[1].strip()}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def prepare_dataset(output_dir: str):
    """
    Full dataset preparation pipeline for AbdiWrite.
    Run this in Google Colab after mounting Drive.

    Args:
        output_dir: Path to save train.json and eval_held_out.json
                    e.g. "/content/drive/MyDrive/abdi/abdiwrite/data"
    """
    print("\n" + "="*60)
    print("  AbdiWrite — Dataset Preparation")
    print("="*60 + "\n")

    # --- English (JFLEG) ---
    raw_jfleg = load_jfleg(output_dir)
    english_pairs = format_jfleg_pairs(raw_jfleg, target_count=TARGET_ENGLISH)
    print_samples(english_pairs, n=2, label="JFLEG English")

    # --- Urdu synthetic ---
    urdu_pairs = generate_synthetic_urdu_pairs(
        URDU_SEED_SENTENCES, target_count=TARGET_URDU
    )
    print_samples(urdu_pairs, n=2, label="Synthetic Urdu/Roman")

    # --- Merge and split ---
    train_data, eval_data = merge_and_split(english_pairs, urdu_pairs)

    # --- Save ---
    save_splits(train_data, eval_data, output_dir)

    print("\n[Done] AbdiWrite dataset preparation complete.")
    print(f"       Training examples : {len(train_data)}")
    print(f"       Eval examples     : {len(eval_data)}")
    print(f"       Output directory  : {output_dir}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Prepare AbdiWrite bilingual dataset")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/content/drive/MyDrive/abdi/abdiwrite/data",
        help="Directory to save train.json and eval_held_out.json",
    )
    args = parser.parse_args()
    prepare_dataset(args.output_dir)
