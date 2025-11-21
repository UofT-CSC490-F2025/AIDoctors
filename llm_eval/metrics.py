from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

def score_predictions(y_true: np.ndarray,
                      y_pred_labels: List[str],
                      label_order: List[str]) -> Dict[str, Any]:
    mask_valid = np.array([p in label_order for p in y_pred_labels])
    y_true_valid = y_true[mask_valid]
    y_pred_valid = np.array(y_pred_labels)[mask_valid]

    macro_f1 = f1_score(y_true_valid, y_pred_valid, average="macro") if len(y_true_valid) else 0.0
    acc = accuracy_score(y_true_valid, y_pred_valid) if len(y_true_valid) else 0.0
    parse_rate = float(mask_valid.mean()) if len(mask_valid) else 0.0

    report = classification_report(y_true_valid, y_pred_valid, target_names=label_order, digits=3, zero_division=0)
    cm = confusion_matrix(y_true_valid, y_pred_valid, labels=label_order)

    return {
        "macro_f1": macro_f1,
        "accuracy": acc,
        "parse_rate": parse_rate,
        "report": report,
        "cm": cm.tolist(),
        "valid_counts": int(mask_valid.sum()),
        "total_counts": int(len(mask_valid)),
    }

def plot_confusion(cm: np.ndarray, labels: List[str], out_path: str):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted"); plt.ylabel("True"); plt.title("LLM Confusion Matrix (valid preds only)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def save_eval(pred_df: pd.DataFrame, summary: Dict[str, Any], out_dir: str):
    pred_path = os.path.join(out_dir, "predictions.csv")
    pred_df.to_csv(pred_path, index=False)

    with open(os.path.join(out_dir, "eval.json"), "w") as f:
        json.dump(summary, f, indent=2)
