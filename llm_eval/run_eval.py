import os
import time
import argparse
from typing import List
import numpy as np
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style, init

from .config import OUT_DIR, TEMPERATURE, TOP_P, MAX_TOKENS
from .data import load_and_prepare, split_indices
from .prompts import SYSTEM_PROMPT, build_user_prompt, extract_severity
from .bedrock_client import converse
from .metrics import score_predictions, plot_confusion, save_eval

init(autoreset=True)

def make_shards(indices: List[int], shards: int) -> List[List[int]]:
    parts = [[] for _ in range(shards)]
    for i, idx in enumerate(indices):
        parts[i % shards].append(idx)
    return parts

def main():
    parser = argparse.ArgumentParser(description="Sharded LLM eval to avoid token expiry")
    parser.add_argument("--shard", type=int, default=0, help="Which shard to run (0-based)")
    parser.add_argument("--shards", type=int, default=3, help="Total number of shards")
    parser.add_argument("--save-shards", action="store_true", help="Write shard index files to data/llm_eval_splits/")
    args = parser.parse_args()

    if not (0 <= args.shard < args.shards):
        raise SystemExit(f"--shard must be in [0..{args.shards-1}]")

    print(Fore.CYAN + f"\n=== LLM Evaluation (shard {args.shard}/{args.shards-1}) ===\n" + Style.RESET_ALL)

    print(Fore.YELLOW + "[Step 1/6] Loading dataset & splitting..." + Style.RESET_ALL)
    df = load_and_prepare()
    idx_train, idx_val, idx_test, y_train, y_val, y_test, le = split_indices(df)

    test_indices_all: List[int] = list(idx_test.values)
    shards = make_shards(test_indices_all, args.shards)
    test_indices = shards[args.shard]
    print(Fore.GREEN + f"Total test examples: {len(test_indices_all)}  |  This shard: {len(test_indices)}" + Style.RESET_ALL)

    if args.save_shards:
        split_dir = os.path.join("data", "llm_eval_splits")
        os.makedirs(split_dir, exist_ok=True)
        for s, part in enumerate(shards):
            pd.Series(part, name="index").to_csv(
                os.path.join(split_dir, f"test_indices_part{s}.csv"), index=False
            )
        print(Fore.GREEN + f"Wrote shard index files to {split_dir}" + Style.RESET_ALL)

    print(Fore.YELLOW + "[Step 2/6] Querying Bedrock for this shard..." + Style.RESET_ALL)
    preds: List[str] = []
    raw_texts: List[str] = []

    start_time = time.time()
    for i, idx in enumerate(test_indices, 1):
        row = df.loc[idx]
        drug1 = row.get("drug1_norm") or row.get("drug1")
        drug2 = row.get("drug2_norm") or row.get("drug2")

        print(Fore.CYAN + f"\n─── Example {i}/{len(test_indices)} (global idx {idx}) ───" + Style.RESET_ALL)
        print(f"{Fore.MAGENTA}Drugs: {drug1} + {drug2}{Style.RESET_ALL}")

        user_prompt = build_user_prompt(row)
        print(Fore.YELLOW + "\n[Prompt → LLM]:" + Style.RESET_ALL)
        print(user_prompt[:800] + ("..." if len(user_prompt) > 800 else ""))

        try:
            response_text = converse(
                user_text=user_prompt,
                system_text=SYSTEM_PROMPT,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_tokens=MAX_TOKENS,
            )
        except Exception as e:
            print(Fore.RED + f"⚠️ Error during Bedrock call: {e}" + Style.RESET_ALL)
            preds.append(None)
            raw_texts.append("")
            continue

        print(Fore.CYAN + "\n[Model Response]:" + Style.RESET_ALL)
        print(response_text.strip()[:800] + ("..." if len(response_text) > 800 else ""))

        sev = extract_severity(response_text)
        preds.append(sev if sev in le.classes_.tolist() else None)
        raw_texts.append(response_text)
        print(Fore.GREEN + f"\n✅ Extracted Severity: {sev}\n" + Style.RESET_ALL)

        time.sleep(0.3)  

    elapsed = time.time() - start_time
    print(Fore.GREEN + f"\n✅ Shard inference finished in {elapsed/60:.2f} min\n" + Style.RESET_ALL)

    label_lookup = pd.Series(le.inverse_transform(y_test), index=list(idx_test.values))  
    true_labels = label_lookup.loc[test_indices].values

    print(Fore.YELLOW + "[Step 3/6] Scoring shard..." + Style.RESET_ALL)
    safe_preds = [p if p is not None else "__INVALID__" for p in preds]
    summary = score_predictions(np.array(true_labels), safe_preds, le.classes_.tolist())

    print(Fore.YELLOW + "[Step 4/6] Saving shard outputs..." + Style.RESET_ALL)
    shard_tag = f"part{args.shard}_of{args.shards}"
    pred_df = pd.DataFrame({
        "index": test_indices,
        "true": true_labels,
        "pred": [p if p in le.classes_.tolist() else "Invalid" for p in preds],
        "raw": raw_texts
    })
    os.makedirs(OUT_DIR, exist_ok=True)
    pred_path = os.path.join(OUT_DIR, f"predictions_{shard_tag}.csv")
    pred_df.to_csv(pred_path, index=False)

    cm_path = os.path.join(OUT_DIR, f"confusion_matrix_{shard_tag}.png")
    plot_confusion(np.array(summary["cm"]), le.classes_.tolist(), cm_path)

    shard_eval_path = os.path.join(OUT_DIR, f"eval_{shard_tag}.json")
    import json
    with open(shard_eval_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(Fore.YELLOW + "[Step 5/6] Shard summary:" + Style.RESET_ALL)
    print(Fore.GREEN + f"Macro F1: {summary['macro_f1']:.4f} | "
                       f"Accuracy: {summary['accuracy']:.4f} | "
                       f"Parse rate: {summary['parse_rate']:.2%}" + Style.RESET_ALL)
    print("\n" + summary["report"])

    print(Fore.CYAN + f"\nSaved files:" + Style.RESET_ALL)
    print(f" - {pred_path}")
    print(f" - {cm_path}")
    print(f" - {shard_eval_path}")

    print(Fore.CYAN + "\n=== ✅ Shard run complete ===\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
