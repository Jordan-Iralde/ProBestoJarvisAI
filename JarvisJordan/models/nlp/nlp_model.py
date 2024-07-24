from transformers import pipeline

nlp_model = pipeline('text-generation', model='gpt-2')

def generate_response(query):
    response = nlp_model(query, max_length=50)[0]['generated_text']
    return response
