import sys
sys.path.append('../')

from dataset.load_dataset import format_dataset
import logging
import argparse
import datasets
from datasets import DatasetDict, load_dataset
from peft import LoraConfig
import torch
import transformers
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig

import env

def finetune(model, nb_training_examples=3900, nb_epochs=1, unk_pad_token=False):
    logger = logging.getLogger(__name__)

    ###################
    # Hyper-parameters
    ###################
    training_config = {
        "bf16": True,
        "do_eval": False,
        "learning_rate": 5.0e-06,
        "log_level": "info",
        "logging_steps": 20,
        "logging_strategy": "steps",
        "lr_scheduler_type": "cosine",
        "num_train_epochs": nb_epochs,
        "max_steps": -1,
        "output_dir": f"{env.tmp_fodler}/{model}/e{nb_epochs}-n{nb_training_examples}/checkpoints",
        "overwrite_output_dir": True,
        "per_device_eval_batch_size": 1,
        "per_device_train_batch_size": 1,
        "remove_unused_columns": True,
        "save_steps": 500,
        "save_total_limit": 10,
        "seed": 0,
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs":{"use_reentrant": False},
        "gradient_accumulation_steps": 1,
        "warmup_ratio": 0.2,
    }

    peft_config = {
        "r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "bias": "none",
        "task_type": "CAUSAL_LM",
        "target_modules": "all-linear",
        "modules_to_save": None,
    }
    train_conf = TrainingArguments(**training_config)
    peft_conf = LoraConfig(**peft_config)


    ###############
    # Setup logging
    ###############
    print("configuring logging...")
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log_level = train_conf.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process a small summary
    logger.warning(
        f"Process rank: {train_conf.local_rank}, device: {train_conf.device}, n_gpu: {train_conf.n_gpu}"
        + f" distributed training: {bool(train_conf.local_rank != -1)}, 16-bits training: {train_conf.fp16}"
    )
    logger.info(f"Training/evaluation parameters {train_conf}")
    logger.info(f"PEFT parameters {peft_conf}")


    ################
    # Model Loading
    ################

    checkpoint_path = env.models_folder + "/" + model
    model_kwargs = dict(
        use_cache=False,
        trust_remote_code=True,
        attn_implementation="eager",
        torch_dtype=torch.bfloat16,
        device_map=None
    )
    model = AutoModelForCausalLM.from_pretrained(checkpoint_path, **model_kwargs)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    tokenizer.model_max_length = 4096
    if unk_pad_token:
        tokenizer.pad_token = tokenizer.unk_token  # use unk rather than eos token to prevent endless generation
        tokenizer.pad_token_id = tokenizer.convert_tokens_to_ids(tokenizer.pad_token)
        tokenizer.padding_side = 'right'


    ##################
    # Data Processing
    ##################
    def apply_chat_template(
        example,
        tokenizer,
    ):
        example["text"] = tokenizer.apply_chat_template(
            example["text"], tokenize=False, add_generation_prompt=False)
        return example

    train_dataset = format_dataset("train", nb_training_examples, True)
    test_dataset = format_dataset("validation", 200, True)
    # raw_dataset: DatasetDict = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)
    # test_dataset = raw_dataset["validation"].select(range(1000))
    # column_names = list(train_dataset.features)

    processed_train_dataset = train_dataset.map(
        apply_chat_template,
        fn_kwargs={"tokenizer": tokenizer},
        num_proc=10,
        desc="Applying chat template to train",
    )

    processed_test_dataset = test_dataset.map(
        apply_chat_template,
        fn_kwargs={"tokenizer": tokenizer},
        num_proc=10,
        desc="Applying chat template to validation",
    )


    ###########
    # Training
    ###########
    trainer = SFTTrainer(
        model=model,
        args=train_conf,
        peft_config=peft_conf,
        train_dataset=processed_train_dataset,
        eval_dataset=processed_test_dataset,
        max_seq_length=4096,
        dataset_text_field="text",
        tokenizer=tokenizer,
        packing=False
    )
    train_result = trainer.train()
    metrics = train_result.metrics
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()


    #############
    # Evaluation
    #############
    tokenizer.padding_side = 'left'
    metrics = trainer.evaluate()
    metrics["eval_samples"] = len(test_dataset)
    trainer.log_metrics("eval", metrics)
    trainer.save_metrics("eval", metrics)


    # ############
    # # Save model
    # ############
    trainer.save_model(train_conf.output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--nb_examples", type=int)
    parser.add_argument("--unk_pad_token", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    finetune(args.model, args.nb_examples, args.epochs, args.unk_pad_token)
