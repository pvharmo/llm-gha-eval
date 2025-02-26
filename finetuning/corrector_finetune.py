import sys
sys.path.append('../')

from dataset.load_dataset import format_dataset
import argparse
from trl import SFTTrainer

from finetuning_utils import load_model, config
import env

def finetune(model, nb_training_examples=None, nb_epochs=1, dataset=None, split="generator_train"):
    output_dir = f"{env.tmp_fodler}/{model}/e{nb_epochs}-n{nb_training_examples if nb_training_examples is not None else 'All'}"
    train_conf, peft_conf = config(output_dir, nb_epochs)
    model, tokenizer = load_model(model)

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

    if dataset is None:
        train_dataset = format_dataset(split, with_answers=True)
        validation_dataset = format_dataset("validation", 200, True)
    else:
        train_dataset = dataset[split]
        validation_dataset = dataset["validation"]

    processed_train_dataset = train_dataset.map(
        apply_chat_template,
        fn_kwargs={"tokenizer": tokenizer},
    )

    processed_validation_dataset = validation_dataset.map(
        apply_chat_template,
        fn_kwargs={"tokenizer": tokenizer},
    )

    ###########
    # Training
    ###########
    trainer = SFTTrainer(
        model=model,
        args=train_conf,
        peft_config=peft_conf,
        train_dataset=processed_train_dataset,
        eval_dataset=processed_validation_dataset,
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
    metrics["eval_samples"] = len(validation_dataset)
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
    args = parser.parse_args()

    finetune(args.model, None, args.epochs)
