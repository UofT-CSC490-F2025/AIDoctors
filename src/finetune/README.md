# Fine-tuning Qwen3-0.6B with Modal

This project fine-tunes the Qwen3-0.6B language model using Supervised Fine-Tuning (SFT) on Modal's cloud infrastructure with GPU acceleration.

## Overview

The fine-tuning pipeline uses:

-   **Model**: Qwen/Qwen3-0.6B
-   **Framework**: Hugging Face Transformers + TRL (Transformer Reinforcement Learning)
-   **Infrastructure**: Modal with 2x A100-40GB GPUs
-   **Training Method**: Supervised Fine-Tuning (SFT)

## Prerequisites

1. **Python**: >= 3.12
2. **Modal Account**: Sign up at [modal.com](https://modal.com)
3. **Modal CLI**: Install and authenticate
    ```bash
    pip install modal
    modal setup
    ```

## Installation

Install dependencies using `uv` (recommended) or `pip`:

```bash
# Using uv
uv sync

# Or using pip
pip install -r pyproject.toml
```

## Dataset Format

The training data should be in `dataset.json` as a JSONL file (one JSON object per line). Each line should contain a training example in the format expected by your model.

## Training Configuration

The training is configured with the following parameters:

-   **GPUs**: 2x A100-40GB
-   **Training epochs**: 1
-   **Batch size per device**: 4
-   **Gradient accumulation steps**: 4
-   **Effective batch size**: 32 (4 × 4 × 2 GPUs)
-   **Learning rate**: 2e-5
-   **Max steps**: 200
-   **Precision**: FP16
-   **Optimization**: AdamW (fused)
-   **Memory optimization**: Gradient checkpointing enabled

## Usage

### 1. Prepare Your Dataset

Place your training data in `dataset.json` in JSONL format.

### 2. Run Training

Execute the training job on Modal:

```bash
modal run main.py
```

This will:

1. Upload your dataset to Modal
2. Spin up 2x A100 GPUs
3. Train the model for the specified steps
4. Save the fine-tuned model to a persistent Modal volume

### 3. Download the Fine-tuned Model

After training completes, download your model:

```bash
modal volume get sft-models qwen3-0.6b-sft
```

The model will be saved to the `qwen3-0.6b-sft/` directory locally.

## Model Storage

The fine-tuned model is stored in a persistent Modal volume named `sft-models`. This ensures your model persists between runs and can be accessed later.

To list all files in the volume:

```bash
modal volume ls sft-models
```
