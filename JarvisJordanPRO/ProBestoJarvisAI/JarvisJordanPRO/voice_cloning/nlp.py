from transformers import GPT2LMHeadModel, GPT2Tokenizer

def generate_response(prompt, model_name='gpt2'):
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    inputs = tokenizer(prompt, return_tensors='pt')
    outputs = model.generate(inputs['input_ids'], max_length=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
