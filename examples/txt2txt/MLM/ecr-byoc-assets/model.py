import os
from djl_python import Input, Output
import deepspeed
import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

model_id = "EleutherAI/gpt-neo-2.7B"
tensor_parallel = 2

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

model = deepspeed.init_inference(
    model,
    mp_size=tensor_parallel,
    dtype=torch.float16,
    replace_method="auto",
    replace_with_kernel_inject=True,
)

generator = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, device=model.device
)

def handle(inputs: Input) -> None:
    if not inputs.is_empty():
        data = inputs.get_as_json()
        
        input_text = data.get("text", "")
        max_length = data.get("max_length", 50)
        num_return_sequences = data.get("num_return_sequences", 1)
        
        generated_text = generator(
            input_text,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
        )
        
        result = []
        for output in generated_text:
            result.append(output["generated_text"])
        
        return Output().add_as_json(result)
    
    return None
