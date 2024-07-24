import torchaudio

voice_model = torchaudio.pipelines.TACOTRON2_WAVEGLOW

def generate_voice(text):
    waveform, sample_rate, _, _ = voice_model(text)
    torchaudio.save('output.wav', waveform, sample_rate)
    return 'output.wav'
