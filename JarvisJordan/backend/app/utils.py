from .models import OffensiveWord
import re
from transformers import pipeline
import torchaudio
import dlib

# Initialize models
nlp_model = pipeline('text-generation', model='gpt-2')
voice_model = torchaudio.pipelines.TACOTRON2_WAVEGLOW
face_detector = dlib.get_frontal_face_detector()

def process_query(query):
    # Filter offensive words
    offensive_words = OffensiveWord.objects.values_list('word', flat=True)
    for word in offensive_words:
        query = re.sub(f'\\b{word}\\b', '[CENSORED]', query, flags=re.IGNORECASE)
    # Generate response
    response = nlp_model(query, max_length=50)[0]['generated_text']
    return response

def generate_voice(text):
    # Generate voice from text
    waveform, sample_rate, _, _ = voice_model(text)
    torchaudio.save('output.wav', waveform, sample_rate)
    return 'output.wav'

def recognize_face(image_path):
    # Recognize face from image
    image = dlib.load_rgb_image(image_path)
    dets = face_detector(image, 1)
    return [{'left': d.left(), 'top': d.top(), 'right': d.right(), 'bottom': d.bottom()} for d in dets]
