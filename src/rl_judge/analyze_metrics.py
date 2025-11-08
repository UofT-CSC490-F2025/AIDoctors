#!/usr/bin/env python3
"""
Utility script to analyze GRPO training metrics
Usage: python analyze_metrics.py /path/to/checkpoint_dir
"""

import json
import sys
import os
from pathlib import Path


def load_metrics(checkpoint_dir):
    """Load all metric files from checkpoint directory"""
    metrics_file = Path(checkpoint_dir) / "training_metrics.json"
    history_file = Path(checkpoint_dir) / "training_history.json"
    
    if not metrics_file.exists():
        print(f"Error: {metrics_file} not found")
        return None, None
    
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    history = None
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    return metrics, history


def print_summary(metrics):
    """Print a formatted summary of training metrics"""
    print("\n" + "="*70)
    print(" GRPO TRAINING METRICS SUMMARY")
    print("="*70)
    
    # Training section
    print("\n📊 TRAINING METRICS:")
    print("-" * 70)
    training = metrics.get("training", {})
    if training:
        runtime_hours = training.get("train_runtime", 0) / 3600
        print(f"  Training Time:        {runtime_hours:.2f} hours")
        print(f"  Final Loss:           {training.get('train_loss', 'N/A'):.4f}")
        print(f"  Samples/Second:       {training.get('train_samples_per_second', 'N/A'):.2f}")
        print(f"  Steps/Second:         {training.get('train_steps_per_second', 'N/A'):.2f}")
        print(f"  Epochs Completed:     {training.get('epoch', 'N/A'):.1f}")
    
    # Evaluation section
    print("\n📈 EVALUATION METRICS:")
    print("-" * 70)
    evaluation = metrics.get("evaluation", {})
    if evaluation:
        sw_p_at_k = evaluation.get("sw_p_at_k", 0)
        accuracy = evaluation.get("overall_accuracy", 0)
        k = evaluation.get("k", 0)
        num_eval = evaluation.get("num_evaluated", 0)
        
        print(f"  SW-P@{k}:              {sw_p_at_k:.4f} {'⭐' if sw_p_at_k > 0.8 else '📊'}")
        print(f"  Overall Accuracy:     {accuracy:.4f} ({accuracy*100:.1f}%)")
        print(f"  Examples Evaluated:   {num_eval}")
    
    # Per-severity section
    print("\n🎯 PER-SEVERITY PERFORMANCE:")
    print("-" * 70)
    per_severity = metrics.get("per_severity", {})
    for severity in ["Major", "Moderate", "Minor"]:
        if severity in per_severity:
            sev_data = per_severity[severity]
            acc = sev_data.get("accuracy", 0)
            count = sev_data.get("count", 0)
            bar = "█" * int(acc * 20)
            print(f"  {severity:12s}  {acc:.4f} ({acc*100:.1f}%)  {bar}  [n={count}]")
    
    # Configuration section
    print("\n⚙️  CONFIGURATION:")
    print("-" * 70)
    config = metrics.get("config", {})
    if config:
        print(f"  Model:                {config.get('model_name', 'N/A')}")
        print(f"  Learning Rate:        {config.get('learning_rate', 'N/A')}")
        print(f"  Batch Size:           {config.get('batch_size', 'N/A')}")
        print(f"  Epochs:               {config.get('num_train_epochs', 'N/A')}")
        print(f"  Gradient Accum:       {config.get('gradient_accumulation_steps', 'N/A')}")
    
    print("\n" + "="*70)


def print_best_predictions(metrics, n=5):
    """Print the best predictions"""
    samples = metrics.get("sample_predictions", [])
    if not samples:
        return
    
    print(f"\n🏆 TOP {n} PREDICTIONS (by reward):")
    print("="*70)
    
    sorted_samples = sorted(samples, key=lambda x: x.get('reward', 0), reverse=True)
    
    for i, sample in enumerate(sorted_samples[:n], 1):
        print(f"\n[{i}] Example {sample.get('idx', 'N/A')}")
        print(f"    Predicted: {sample.get('predicted', 'N/A'):10s}  Actual: {sample.get('actual', 'N/A'):10s}  "
              f"Reward: {sample.get('reward', 0):.3f}")
        prompt = sample.get('prompt', '')
        if len(prompt) > 100:
            prompt = prompt[:100] + "..."
        print(f"    Prompt: {prompt}")
        print(f"    Correct: {'✓' if sample.get('correct') else '✗'}")


def print_training_progress(history):
    """Print training progress summary"""
    if not history:
        return
    
    print("\n📉 TRAINING PROGRESS:")
    print("="*70)
    
    losses = [(entry.get('step', 0), entry.get('loss', 0)) 
              for entry in history if 'loss' in entry]
    
    if losses:
        print(f"  Total training steps: {losses[-1][0]}")
        print(f"  Initial loss:         {losses[0][1]:.4f}")
        print(f"  Final loss:           {losses[-1][1]:.4f}")
        print(f"  Loss improvement:     {(losses[0][1] - losses[-1][1]):.4f} "
              f"({((losses[0][1] - losses[-1][1])/losses[0][1]*100):.1f}% reduction)")
        
        # Find best loss
        best_loss = min(losses, key=lambda x: x[1])
        print(f"  Best loss:            {best_loss[1]:.4f} (step {best_loss[0]})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_metrics.py /path/to/checkpoint_dir")
        sys.exit(1)
    
    checkpoint_dir = sys.argv[1]
    
    if not os.path.isdir(checkpoint_dir):
        print(f"Error: {checkpoint_dir} is not a directory")
        sys.exit(1)
    
    print(f"\nAnalyzing metrics from: {checkpoint_dir}")
    
    metrics, history = load_metrics(checkpoint_dir)
    
    if metrics is None:
        sys.exit(1)
    
    print_summary(metrics)
    print_best_predictions(metrics, n=5)
    print_training_progress(history)
    
    print("\n✨ Analysis complete!")
    print(f"\n💡 Tip: View detailed plots with:")
    print(f"   tensorboard --logdir={checkpoint_dir}/runs")
    print()


if __name__ == "__main__":
    main()
