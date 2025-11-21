import subprocess
import modal

# Create a persistent image with a name so it doesn't rebuild every time
image = (
    modal.Image.from_registry("nvidia/cuda:13.0.2-devel-ubuntu24.04", add_python="3.13")
    .pip_install("datasets", "transformers", "trl", "accelerate", "peft", "bitsandbytes")
)

app = modal.App("Custom SFT Training")

# Create a persistent volume to store the fine-tuned model
volume = modal.Volume.from_name("sft-models", create_if_missing=True)

@app.function(
    gpu="A100-40GB:2",  # 2 GPUs is optimal for small datasets
    timeout=7200,
    volumes={"/models": volume},  # Mount volume at /models
    image=image,
)
def trainSFT(dataset_json):

    from datasets import load_dataset, Dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments
    
    # Training arguments optimized for 2-GPU training
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=1,
        per_device_train_batch_size=4,   # Increased batch size per GPU
        gradient_accumulation_steps=4,    # Effective batch size = 4 * 4 * 2 GPUs = 32
        learning_rate=2e-5,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        max_steps=200,  # Reduced from 1000 for faster training
        ddp_find_unused_parameters=False,
        gradient_checkpointing=True,      # Save memory
        optim="adamw_torch_fused",        # More memory efficient
    )
    
    dataset = Dataset.from_list(dataset_json)
    
    trainer = SFTTrainer(
        model="Qwen/Qwen3-0.6B",
        train_dataset=dataset,
        args=training_args
    )
    trainer.train()
    
    # Save the fine-tuned model to the persistent volume
    output_dir = "/models/qwen3-0.6b-sft"
    trainer.save_model(output_dir)
    trainer.tokenizer.save_pretrained(output_dir)
    
    # Commit changes to the volume so they persist
    volume.commit()
    
    print(f"Model saved to Modal Volume at {output_dir}")
    print("To download the model, use: modal volume get sft-models qwen3-0.6b-sft")
    
    return output_dir


@app.local_entrypoint()
def main():
    import json
    # Load JSONL file (one JSON object per line)
    dataset_json = []
    with open("dataset.json", "r") as f:
        for line in f:
            dataset_json.append(json.loads(line))
    
    print(f"Loaded {len(dataset_json)} examples from dataset.json")
    
    # Run the training function with the dataset
    trainSFT.remote(dataset_json)