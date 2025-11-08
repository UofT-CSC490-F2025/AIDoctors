"""
Reinforcement Learning with Verifiable Rewards (RLVR) using GRPO
Fine-tunes a model to predict drug-drug interaction severity
Uses Hugging Face TRL and Transformers with Modal for distributed training
"""

import modal
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from datasets import Dataset
import torch
import json
import re
from typing import List, Dict, Tuple
import numpy as np
import os

# Define Modal app and image
app = modal.App("rl-ddi-severity-grpo")

# Create Modal image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "trl",
        "datasets",
        "accelerate",
        "bitsandbytes",
        "peft",
        "numpy",
        "tensorboard",  # For training visualization
        "matplotlib",   # For plotting metrics
        "seaborn",      # For better visualizations
    )
)

# Define Modal volume for model checkpoints
volume = modal.Volume.from_name("rl-model-checkpoints", create_if_missing=True)

# Define Modal volume for datasets
data_volume = modal.Volume.from_name("rl-datasets", create_if_missing=True)

# Severity weights for SW-P@k calculation
SEVERITY_WEIGHTS = {
    "Major": 3.0,
    "Moderate": 2.0,
    "Minor": 1.0,
    "Unknown": 0.0
}

def extract_severity(text: str) -> str:
    """
    Extract severity from model output
    Expects JSON format: {"severity": "Major|Moderate|Minor"}
    """
    try:
        # Try to parse as JSON
        match = re.search(r'\{[^}]*"severity"\s*:\s*"([^"]+)"[^}]*\}', text, re.IGNORECASE)
        if match:
            severity = match.group(1).strip()
            # Normalize severity
            severity_lower = severity.lower()
            if "major" in severity_lower:
                return "Major"
            elif "moderate" in severity_lower:
                return "Moderate"
            elif "minor" in severity_lower:
                return "Minor"
            return "Unknown"
    except:
        pass
    return "Unknown"

def calculate_severity_reward(predicted: str, actual: str) -> float:
    """
    Calculate reward based on severity prediction accuracy
    Uses weighted scoring where Major > Moderate > Minor
    
    Returns:
        Reward between 0.0 and 1.0
    """
    predicted = predicted.strip()
    actual = actual.strip()
    
    # Exact match gets full reward based on severity weight
    if predicted == actual:
        base_reward = SEVERITY_WEIGHTS.get(actual, 0.0) / SEVERITY_WEIGHTS["Major"]
        return base_reward
    
    # Partial credit for close predictions
    severity_order = ["Minor", "Moderate", "Major"]
    
    if predicted in severity_order and actual in severity_order:
        pred_idx = severity_order.index(predicted)
        actual_idx = severity_order.index(actual)
        distance = abs(pred_idx - actual_idx)
        
        # 1 level off: 50% credit, 2 levels off: 25% credit
        if distance == 1:
            return 0.5 * (SEVERITY_WEIGHTS.get(actual, 0.0) / SEVERITY_WEIGHTS["Major"])
        elif distance == 2:
            return 0.25 * (SEVERITY_WEIGHTS.get(actual, 0.0) / SEVERITY_WEIGHTS["Major"])
    
    # Wrong prediction
    return 0.0

def calculate_sw_p_at_k(predictions: List[str], actuals: List[str], k: int = None) -> float:
    """
    Calculate Severity-Weighted Precision at K (SW-P@k)
    
    Args:
        predictions: List of predicted severities
        actuals: List of actual severities
        k: Number of top alerts to consider (if None, use all)
    
    Returns:
        SW-P@k score
    """
    if k is None:
        k = len(predictions)
    
    k = min(k, len(predictions))
    
    weighted_scores = []
    for pred, actual in zip(predictions[:k], actuals[:k]):
        reward = calculate_severity_reward(pred, actual)
        weighted_scores.append(reward)
    
    return np.mean(weighted_scores) if weighted_scores else 0.0

def plot_training_metrics(log_history: List[Dict], output_dir: str):
    """
    Plot training metrics from the log history
    
    Args:
        log_history: Trainer's log history
        output_dir: Directory to save plots
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        sns.set_style("whitegrid")
        
        # Extract metrics from log history
        steps = []
        losses = []
        learning_rates = []
        rewards = []
        
        for entry in log_history:
            if 'loss' in entry:
                steps.append(entry.get('step', 0))
                losses.append(entry['loss'])
            if 'learning_rate' in entry:
                learning_rates.append(entry['learning_rate'])
            if 'reward' in entry:
                rewards.append(entry['reward'])
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('GRPO Training Metrics', fontsize=16, fontweight='bold')
        
        # Plot loss
        if losses:
            axes[0, 0].plot(steps, losses, linewidth=2, color='#2E86AB')
            axes[0, 0].set_title('Training Loss', fontsize=12, fontweight='bold')
            axes[0, 0].set_xlabel('Step')
            axes[0, 0].set_ylabel('Loss')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Plot learning rate
        if learning_rates:
            axes[0, 1].plot(learning_rates, linewidth=2, color='#A23B72')
            axes[0, 1].set_title('Learning Rate Schedule', fontsize=12, fontweight='bold')
            axes[0, 1].set_xlabel('Step')
            axes[0, 1].set_ylabel('Learning Rate')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot rewards
        if rewards:
            axes[1, 0].plot(rewards, linewidth=2, color='#F18F01')
            axes[1, 0].set_title('Average Reward', fontsize=12, fontweight='bold')
            axes[1, 0].set_xlabel('Step')
            axes[1, 0].set_ylabel('Reward')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot loss moving average
        if len(losses) > 10:
            window = min(10, len(losses) // 10)
            loss_ma = np.convolve(losses, np.ones(window)/window, mode='valid')
            steps_ma = steps[window-1:]
            axes[1, 1].plot(steps_ma, loss_ma, linewidth=2, color='#C73E1D')
            axes[1, 1].set_title(f'Loss (Moving Avg, window={window})', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('Step')
            axes[1, 1].set_ylabel('Loss (MA)')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(output_dir, 'training_metrics.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Training metrics plot saved to {plot_path}")
        
    except Exception as e:
        print(f"Warning: Could not generate plots: {e}")

@app.function(image=image, volumes={"/data": data_volume})
def prepare_ddi_dataset(
    raw_data: List[Dict],
    output_path: str = "/data/ddi_training_data.json"
) -> str:
    """
    Prepare DDI dataset with reward signals for GRPO training
    
    Args:
        raw_data: List of dictionaries containing prompt and completion data
        output_path: Path to save processed dataset
    
    Returns:
        Path to saved dataset
    """
    print(f"Processing {len(raw_data)} raw data items...")
    
    training_data = []
    
    for idx, item in enumerate(raw_data):
        # Extract prompt (user message)
        prompt_content = item.get("prompt", [{}])[0].get("content", "")
        
        # Extract completion (assistant message with severity)
        completion_content = item.get("completion", [{}])[0].get("content", "")
        
        # Extract actual severity from completion
        actual_severity = extract_severity(completion_content)
        
        if not prompt_content or actual_severity == "Unknown":
            continue
        
        # Store data for GRPO training
        training_data.append({
            "query": prompt_content,
            "reference": completion_content,
            "actual_severity": actual_severity,
            "idx": idx
        })
    
    # Save processed dataset
    with open(output_path, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Processed {len(training_data)} training examples")
    print(f"Dataset saved to {output_path}")
    
    # Commit volume to persist data
    data_volume.commit()
    
    return output_path

def reward_function(completions: List[str], actual_severities: List[str]) -> List[float]:
    """
    Custom reward function for DDI severity prediction
    
    Args:
        completions: List of model-generated completions
        actual_severities: List of ground truth severities
    
    Returns:
        List of reward scores
    """
    rewards = []
    
    for completion, actual in zip(completions, actual_severities):
        predicted_severity = extract_severity(completion)
        reward = calculate_severity_reward(predicted_severity, actual)
        rewards.append(reward)
    
    return rewards

@app.function(
    image=image,
    gpu="A100",
    timeout=14400,  # 4 hours timeout
    volumes={"/checkpoints": volume, "/data": data_volume},
)
def train_rl_agent(
    model_name: str = "Qwen/Qwen2.5-0.5B",
    data_path: str = "/data/ddi_training_data.json",
    output_dir: str = "/checkpoints/grpo_ddi_model",
    num_train_epochs: int = 3,
    learning_rate: float = 5e-6,
    batch_size: int = 4,
    k_for_evaluation: int = 100,
):
    """
    Train a model using GRPO with DDI severity reward signals
    
    Args:
        model_name: Base model to fine-tune
        data_path: Path to processed training data
        output_dir: Directory to save trained model
        num_train_epochs: Number of training epochs
        learning_rate: Learning rate for optimization
        batch_size: Batch size for training
        k_for_evaluation: K value for SW-P@k metric
    """
    
    print(f"Loading model: {model_name}")
    
    # Load base model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id
    
    print("Loading training data...")
    
    # Load training data
    with open(data_path, 'r') as f:
        training_data = json.load(f)
    
    # Prepare dataset for GRPO
    # GRPO expects specific columns: prompt/query and potentially completions
    dataset_dict = {
        "prompt": [item["query"] for item in training_data],
        "actual_severity": [item["actual_severity"] for item in training_data],
    }
    
    dataset = Dataset.from_dict(dataset_dict)
    
    print(f"Dataset size: {len(dataset)}")
    
    # Configure GRPO training with comprehensive logging
    training_config = GRPOConfig(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        
        # Logging configuration
        logging_steps=10,
        logging_first_step=True,
        log_completions=True,  # Log sample completions during training
        num_completions_to_print=5,  # Number of completions to print
        
        # Checkpoint saving
        save_steps=500,
        save_total_limit=3,  # Keep only the last 3 checkpoints
        
        # Evaluation configuration (disabled since we don't have a separate eval set)
        eval_strategy="no",  # Set to "no" since we don't have eval_dataset
        
        # Training optimization
        gradient_accumulation_steps=8,
        warmup_steps=100,
        bf16=True,
        
        # Report metrics to console and files
        report_to=["tensorboard"],  # Can add "wandb" if you have it configured
        
        # Other settings
        remove_unused_columns=False,
        load_best_model_at_end=False,
    )
    
    print("Initializing GRPO Trainer...")
    
    # Create a custom reward function for DDI severity prediction
    # According to GRPO docs, the function must accept:
    # - prompts, completions, completions_ids as keyword arguments
    # - any additional dataset columns (like actual_severity)
    def severity_reward_func(prompts, completions, actual_severity, **kwargs):
        """
        Custom reward function for DDI severity prediction
        
        Args:
            prompts: List of prompt strings
            completions: List of completion strings
            actual_severity: List of ground truth severity labels
            **kwargs: Additional arguments (ignored)
        
        Returns:
            List of reward scores (floats)
        """
        rewards = []
        for completion, actual in zip(completions, actual_severity):
            predicted_severity = extract_severity(completion)
            reward = calculate_severity_reward(predicted_severity, actual)
            rewards.append(reward)
        return rewards
    
    # Initialize GRPO trainer
    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        args=training_config,
        train_dataset=dataset,
        reward_funcs=severity_reward_func,
    )
    
    print("Starting training with RLVR using GRPO...")
    
    # Track training metrics
    training_start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
    training_end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
    
    if training_start_time:
        training_start_time.record()
    
    # Train the model
    train_result = trainer.train()
    
    if training_end_time and training_start_time:
        training_end_time.record()
        torch.cuda.synchronize()
        training_time_ms = training_start_time.elapsed_time(training_end_time)
        training_time_hours = training_time_ms / (1000 * 60 * 60)
        print(f"Training completed in {training_time_hours:.2f} hours")
    
    # Extract training metrics
    training_metrics = {
        "train_runtime": train_result.metrics.get("train_runtime", 0),
        "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
        "train_steps_per_second": train_result.metrics.get("train_steps_per_second", 0),
        "total_flos": train_result.metrics.get("total_flos", 0),
        "train_loss": train_result.metrics.get("train_loss", 0),
        "epoch": train_result.metrics.get("epoch", 0),
    }
    
    print("\n" + "="*50)
    print("Training Metrics Summary:")
    print("="*50)
    for key, value in training_metrics.items():
        print(f"{key}: {value}")
    print("="*50 + "\n")
    
    print("Training completed. Evaluating on validation set...")
    
    # Evaluate SW-P@k on training data (ideally use separate validation set)
    predictions = []
    actuals = []
    prediction_details = []
    
    print(f"Evaluating on {min(k_for_evaluation, len(dataset))} examples...")
    
    for i in range(min(k_for_evaluation, len(dataset))):
        prompt = dataset[i]["prompt"]
        actual_severity = dataset[i]["actual_severity"]
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=False,
            )
        
        completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predicted_severity = extract_severity(completion)
        
        predictions.append(predicted_severity)
        actuals.append(actual_severity)
        
        # Store detailed predictions for analysis
        prediction_details.append({
            "idx": i,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "predicted": predicted_severity,
            "actual": actual_severity,
            "correct": predicted_severity == actual_severity,
            "reward": calculate_severity_reward(predicted_severity, actual_severity)
        })
        
        # Print progress
        if (i + 1) % 10 == 0:
            print(f"Evaluated {i + 1}/{min(k_for_evaluation, len(dataset))} examples")
    
    # Calculate SW-P@k
    sw_p_at_k = calculate_sw_p_at_k(predictions, actuals, k=k_for_evaluation)
    
    # Calculate additional metrics
    accuracy = sum(p == a for p, a in zip(predictions, actuals)) / len(predictions)
    
    # Calculate per-severity metrics
    severity_metrics = {}
    for severity in ["Major", "Moderate", "Minor"]:
        severity_mask = [a == severity for a in actuals]
        if sum(severity_mask) > 0:
            severity_preds = [p for p, m in zip(predictions, severity_mask) if m]
            severity_actuals = [a for a, m in zip(actuals, severity_mask) if m]
            severity_acc = sum(p == a for p, a in zip(severity_preds, severity_actuals)) / len(severity_actuals)
            severity_metrics[severity] = {
                "count": sum(severity_mask),
                "accuracy": severity_acc
            }
    
    print("\n" + "="*50)
    print("Evaluation Metrics:")
    print("="*50)
    print(f"SW-P@{k_for_evaluation}: {sw_p_at_k:.4f}")
    print(f"Overall Accuracy: {accuracy:.4f}")
    print(f"\nPer-Severity Metrics:")
    for severity, metrics in severity_metrics.items():
        print(f"  {severity}: {metrics['accuracy']:.4f} (n={metrics['count']})")
    print("="*50 + "\n")
    
    print("Saving model...")
    
    # Save the trained model
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Save comprehensive evaluation metrics
    metrics = {
        "training": {
            **training_metrics,
        },
        "evaluation": {
            "sw_p_at_k": sw_p_at_k,
            "k": k_for_evaluation,
            "overall_accuracy": accuracy,
            "num_examples": len(dataset),
            "num_evaluated": len(predictions),
        },
        "per_severity": severity_metrics,
        "sample_predictions": prediction_details[:20],  # Save first 20 predictions
        "config": {
            "model_name": model_name,
            "num_train_epochs": num_train_epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "gradient_accumulation_steps": training_config.gradient_accumulation_steps,
        }
    }
    
    # Save metrics to JSON
    metrics_path = f"{output_dir}/training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to {metrics_path}")
    
    # Save training history if available
    if trainer.state.log_history:
        history_path = f"{output_dir}/training_history.json"
        with open(history_path, 'w') as f:
            json.dump(trainer.state.log_history, f, indent=2)
        print(f"Training history saved to {history_path}")
        
        # Generate training plots
        plot_training_metrics(trainer.state.log_history, output_dir)
    
    # Create a summary report
    summary_path = f"{output_dir}/training_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("GRPO Training Summary - DDI Severity Prediction\n")
        f.write("="*60 + "\n\n")
        
        f.write("Model Configuration:\n")
        f.write(f"  Model: {model_name}\n")
        f.write(f"  Epochs: {num_train_epochs}\n")
        f.write(f"  Learning Rate: {learning_rate}\n")
        f.write(f"  Batch Size: {batch_size}\n")
        f.write(f"  Gradient Accumulation: {training_config.gradient_accumulation_steps}\n\n")
        
        f.write("Training Results:\n")
        for key, value in training_metrics.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
        f.write("Evaluation Results:\n")
        f.write(f"  SW-P@{k_for_evaluation}: {sw_p_at_k:.4f}\n")
        f.write(f"  Overall Accuracy: {accuracy:.4f}\n")
        f.write(f"  Examples Evaluated: {len(predictions)}\n\n")
        
        f.write("Per-Severity Performance:\n")
        for severity, metrics_data in severity_metrics.items():
            f.write(f"  {severity}:\n")
            f.write(f"    Accuracy: {metrics_data['accuracy']:.4f}\n")
            f.write(f"    Count: {metrics_data['count']}\n")
        
        f.write("\n" + "="*60 + "\n")
    
    print(f"Training summary saved to {summary_path}")
    
    # Commit the volume to persist checkpoints
    volume.commit()
    
    print(f"Model saved to {output_dir}")
    
    # Print final summary
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Model checkpoint: {output_dir}")
    print(f"Training metrics: {output_dir}/training_metrics.json")
    print(f"Training history: {output_dir}/training_history.json")
    print(f"Summary report: {output_dir}/training_summary.txt")
    print(f"TensorBoard logs: {output_dir}/runs")
    print("="*60)
    
    return {
        "status": "success",
        "output_dir": output_dir,
        "sw_p_at_k": sw_p_at_k,
        "overall_accuracy": accuracy,
        "training_metrics": training_metrics,
        "severity_metrics": severity_metrics,
        "final_loss": trainer.state.log_history[-1].get("loss", None) if trainer.state.log_history else None
    }

@app.function(image=image, gpu="A100", volumes={"/data": data_volume})
def evaluate_model(
    model_path: str,
    data_path: str = "/data/ddi_training_data.json",
    k: int = 100,
    output_path: str = "/tmp/evaluation_results.json"
) -> Dict:
    """
    Evaluate trained model on DDI severity prediction
    
    Args:
        model_path: Path to trained model
        data_path: Path to evaluation data
        k: K value for SW-P@k metric
        output_path: Path to save evaluation results
    
    Returns:
        Evaluation metrics
    """
    print(f"Loading model from {model_path}...")
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
    )
    
    print("Loading evaluation data...")
    
    with open(data_path, 'r') as f:
        eval_data = json.load(f)
    
    predictions = []
    actuals = []
    examples = []
    
    for i, item in enumerate(eval_data[:k]):
        query = item["query"]
        actual_severity = item["actual_severity"]
        reference = item["reference"]
        
        inputs = tokenizer(query, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=False,
            )
        
        completion = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        predicted_severity = extract_severity(completion)
        
        predictions.append(predicted_severity)
        actuals.append(actual_severity)
        
        examples.append({
            "idx": i,
            "predicted": predicted_severity,
            "actual": actual_severity,
            "completion": completion[:500],  # Truncate for readability
            "reward": calculate_severity_reward(predicted_severity, actual_severity)
        })
    
    # Calculate metrics
    sw_p_at_k = calculate_sw_p_at_k(predictions, actuals, k=k)
    
    # Calculate accuracy by severity
    severity_accuracy = {}
    for severity in ["Major", "Moderate", "Minor"]:
        severity_preds = [p for p, a in zip(predictions, actuals) if a == severity]
        severity_actuals = [a for a in actuals if a == severity]
        if severity_actuals:
            accuracy = sum(p == a for p, a in zip(severity_preds, severity_actuals)) / len(severity_actuals)
            severity_accuracy[severity] = accuracy
    
    results = {
        "sw_p_at_k": sw_p_at_k,
        "k": k,
        "total_examples": len(predictions),
        "severity_accuracy": severity_accuracy,
        "sample_predictions": examples[:10],  # First 10 examples
    }
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation Results:")
    print(f"SW-P@{k}: {sw_p_at_k:.4f}")
    print(f"Severity-wise accuracy: {severity_accuracy}")
    
    return results

@app.local_entrypoint()
def main(
    model_name: str = "Qwen/Qwen2.5-0.5B",
    dataset_path: str = "data/joined_data/dataset.json",
    mode: str = "train",  # "train" or "eval"
):
    """
    Main entry point for RLVR training with GRPO
    """
    
    # Load local dataset file (JSONL format - one JSON object per line)
    print(f"Loading local dataset from {dataset_path}...")
    raw_data = []
    with open(dataset_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                raw_data.append(json.loads(line))
    
    print(f"Loaded {len(raw_data)} examples from local file")
    
    if mode == "train":
        print("Starting RLVR training with GRPO for DDI severity prediction...")
        print("=" * 60)
        print("Logging and Metrics Configuration:")
        print("  - TensorBoard logging: ENABLED")
        print("  - Completion logging: ENABLED (5 samples per log)")
        print("  - Metrics tracking: ENABLED")
        print("  - Training plots: ENABLED")
        print("  - Logging frequency: Every 10 steps")
        print("  - Checkpoint saving: Every 500 steps")
        print("=" * 60)
        
        # Prepare dataset (pass data directly to Modal function)
        processed_data_path = prepare_ddi_dataset.remote(
            raw_data=raw_data,
        )
        
        # Train the agent
        result = train_rl_agent.remote(
            model_name=model_name,
            data_path=processed_data_path,
        )
        
        print(f"\nTraining result: {result}")
        
    elif mode == "eval":
        print("Evaluating trained model...")
        
        # Prepare dataset (pass data directly to Modal function)
        processed_data_path = prepare_ddi_dataset.remote(
            raw_data=raw_data,
        )
        
        # Evaluate model
        results = evaluate_model.remote(
            model_path="/checkpoints/grpo_ddi_model",
            data_path=processed_data_path,
            k=100,
        )
        
        print(f"\nEvaluation results: {results}")

if __name__ == "__main__":
    # Run with: modal run rl_judge.py --mode train
    # Or: modal run rl_judge.py --mode eval
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default="Qwen/Qwen2.5-0.5B")
    parser.add_argument('--dataset_path', default="../../data/joined_data/dataset.json")
    parser.add_argument('--mode', default="train", choices=["train", "eval"])
    parser.add_argument('--learning_rate', type=float, default=5e-6)
    parser.add_argument('--num_train_epochs', type=int, default=3)
    
    args = parser.parse_args()
    
    main(
        model_name=args.model_name,
        dataset_path=args.dataset_path,
        mode=args.mode
    )