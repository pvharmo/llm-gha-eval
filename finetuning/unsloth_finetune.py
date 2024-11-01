import sys

from dataset.load_dataset import format_dataset
sys.path.append('../')
import logging
import argparse
import datasets
from datasets import DatasetDict, load_dataset
from unsloth import FastLanguageModel
from unsloth import is_bfloat16_supported
import torch
from trl import SFTTrainer
from transformers import TrainingArguments

import env

def finetune(model, nb_training_examples=3900, nb_epochs=1, max_seq_length = 4096):
    checkpoint_path = env.models_folder + "/" + model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = checkpoint_path,
        max_seq_length = max_seq_length,
        dtype = None,
        load_in_4bit = False,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0, # Supports any, but = 0 is optimized
        bias = "none",    # Supports any, but = "none" is optimized
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
        random_state = 3407,
        max_seq_length = max_seq_length,
        use_rslora = False,  # We support rank stabilized LoRA
        loftq_config = None, # And LoftQ
    )

    dataset = format_dataset("train", nb_training_examples, True)

    trainer = SFTTrainer(
        model = model,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        tokenizer = tokenizer,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 10,
            max_steps = 60,
            fp16 = not is_bfloat16_supported(),
            bf16 = is_bfloat16_supported(),
            logging_steps = 1,
            output_dir = "outputs",
            optim = "adamw_8bit",
            seed = 3407,
        ),
    )
    trainer.train()

    model.save_pretrained_merged(f"{env.tmp_fodler}/{model}", tokenizer, save_method = "merged_16bit",)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    parser.add_argument("--epochs", type=str)
    parser.add_argument("--nb_examples", type=str)
    args = parser.parse_args()

    finetune(args.model, args.nb_examples, args.epochs, 4096)
