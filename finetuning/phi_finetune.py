from finetune import finetune

model = "Phi-3.5-mini-instruct"

finetune(model, unk_pad_token=True)
