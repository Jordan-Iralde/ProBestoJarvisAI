from TTS.api import TTS

def clone_voice(text, model_path='path/to/model'):
    tts = TTS(model_path=model_path)
    tts.tts_to_file(text=text, file_path='output.wav')
