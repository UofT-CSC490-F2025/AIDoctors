# GRPO Training - Logging and Metrics Guide

## Overview
The GRPO training script now includes comprehensive logging and metrics tracking to monitor your training runs.

## Features

### 1. **Console Logging**
- Real-time training progress
- Loss and reward metrics every 10 steps
- Sample completions during training
- Training time tracking
- Evaluation progress updates

### 2. **Metrics Files**

After training, you'll find these files in your checkpoint directory:

#### `training_metrics.json`
Complete metrics including:
- Training statistics (runtime, samples/sec, loss)
- Evaluation results (SW-P@k, accuracy)
- Per-severity performance breakdown
- Sample predictions (first 20)
- Configuration details

#### `training_history.json`
Full training history with step-by-step logs:
- Loss at each logging step
- Learning rate schedule
- Reward signals
- All intermediate metrics

#### `training_summary.txt`
Human-readable summary report:
- Model configuration
- Training results
- Evaluation metrics
- Per-severity performance

### 3. **Visualizations**

#### `training_metrics.png`
4-panel visualization showing:
- Training loss over time
- Learning rate schedule
- Average reward progression
- Loss moving average

### 4. **TensorBoard Integration**

TensorBoard logs are saved in the `runs/` subdirectory of your checkpoint folder.

**To view TensorBoard:**
```bash
# On your local machine (after downloading checkpoints)
tensorboard --logdir=/path/to/checkpoints/grpo_ddi_model/runs

# Then open http://localhost:6006 in your browser
```

**TensorBoard shows:**
- Training loss curves
- Learning rate schedule
- Reward distributions
- Completion examples
- GPU utilization
- All GRPO-specific metrics

## Viewing Metrics During Training

### Real-time Console Output
The script prints metrics every 10 steps:
```
Step 10: loss=2.345, reward=0.567, lr=1e-6
Step 20: loss=2.123, reward=0.623, lr=1.5e-6
...
```

### Sample Completions
Every log interval, you'll see 5 sample completions:
```
Sample Completion 1:
Prompt: [Drug interaction query]
Completion: {"severity": "Major", "explanation": "..."}
Reward: 1.0
```

## Metrics Explained

### Training Metrics
- **train_loss**: Average loss over the epoch
- **train_runtime**: Total training time in seconds
- **train_samples_per_second**: Throughput metric
- **train_steps_per_second**: Training speed
- **total_flos**: Total floating point operations

### Evaluation Metrics
- **sw_p_at_k**: Severity-Weighted Precision at K
- **overall_accuracy**: Percentage of correct predictions
- **per_severity_accuracy**: Accuracy for Major/Moderate/Minor separately

### GRPO-Specific Metrics (in TensorBoard)
- **reward**: Average reward from the reward function
- **reward_std**: Standard deviation of rewards
- **kl**: KL divergence from reference model (if beta > 0)
- **entropy**: Token prediction entropy
- **clip_ratio**: Policy clipping statistics
- **completions**: Sample model outputs

## Customization

### Enable WandB Logging
Add WandB to the `report_to` parameter:

```python
training_config = GRPOConfig(
    ...
    report_to=["tensorboard", "wandb"],
)
```

Then set your WandB API key:
```bash
export WANDB_API_KEY=your_key_here
```

### Adjust Logging Frequency
```python
training_config = GRPOConfig(
    ...
    logging_steps=5,  # Log every 5 steps instead of 10
    num_completions_to_print=10,  # Print 10 samples instead of 5
)
```

### Change Checkpoint Frequency
```python
training_config = GRPOConfig(
    ...
    save_steps=100,  # Save every 100 steps instead of 500
    save_total_limit=5,  # Keep 5 checkpoints instead of 3
)
```

## Accessing Metrics from Modal

After training completes, download your metrics:

```bash
# Download the entire checkpoint directory
modal volume get rl-model-checkpoints grpo_ddi_model ./local_checkpoints/

# View metrics
cat ./local_checkpoints/grpo_ddi_model/training_summary.txt
```

## Troubleshooting

### No TensorBoard logs?
- Check that `report_to=["tensorboard"]` is set
- Ensure the checkpoint directory has write permissions

### Missing plots?
- Verify matplotlib and seaborn are installed
- Check the console for plot generation errors

### WandB not working?
- Verify your API key is set
- Check that `wandb` is installed in the Modal image
- Look for authentication errors in the logs

## Best Practices

1. **Monitor SW-P@k**: This is your primary metric for DDI severity prediction
2. **Watch per-severity accuracy**: Ensure the model isn't biased toward one severity
3. **Check reward trends**: Rewards should generally increase during training
4. **Review sample completions**: Manually inspect to catch formatting issues
5. **Compare checkpoints**: Use metrics to select the best checkpoint

## Example Workflow

```bash
# 1. Start training
python -m modal run src/rl_judge/rl_judge.py --mode train

# 2. Monitor in console (automatic)

# 3. After training, download metrics
modal volume get rl-model-checkpoints grpo_ddi_model ./results/

# 4. View summary
cat ./results/grpo_ddi_model/training_summary.txt

# 5. View detailed metrics
python -c "import json; print(json.dumps(json.load(open('./results/grpo_ddi_model/training_metrics.json')), indent=2))"

# 6. Launch TensorBoard
tensorboard --logdir=./results/grpo_ddi_model/runs
```

## Metrics Schema

### training_metrics.json Structure
```json
{
  "training": {
    "train_runtime": 7234.5,
    "train_loss": 1.234,
    ...
  },
  "evaluation": {
    "sw_p_at_k": 0.789,
    "overall_accuracy": 0.823,
    ...
  },
  "per_severity": {
    "Major": {"count": 150, "accuracy": 0.89},
    "Moderate": {"count": 180, "accuracy": 0.82},
    "Minor": {"count": 123, "accuracy": 0.76}
  },
  "sample_predictions": [...],
  "config": {...}
}
```

## Additional Resources

- [TensorBoard Documentation](https://www.tensorflow.org/tensorboard)
- [TRL GRPO Trainer Metrics](https://huggingface.co/docs/trl/en/grpo_trainer#logged-metrics)
- [WandB Integration](https://docs.wandb.ai/guides/integrations/huggingface)
