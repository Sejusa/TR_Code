!pip install nemo_toolkit['all']
!pip install nemo_text_processing
!pip install pytorch-lightning
!pip install torchaudio

import sys

# Definimos una clase ModelFilter ficticia para satisfacer el requisito de importación
class ModelFilter:
    pass  # Agregamos cualquier atributo o método necesario si lo requiere NeMo

# Agregamos el ModelFilter ficticio a sys.modules
sys.modules['huggingface_hub.ModelFilter'] = ModelFilter

# Ahora podemos importat Nvidia NeMo
import nemo.collections.asr as nemo_asr
import nemo.collections.tts as nemo_tts
import torchaudio
import requests

nemo_asr.models.EncDecCTCModel.list_available_models()

"""
stt_en_quartznet15x5: Este es un modelo QuartzNet que ha demostrado ser muy eficiente para el reconocimiento de voz en inglés. Es una buena opción si tu tarea principal es transcribir audio en inglés.

stt_en_jasper10x5dr: Jasper es otra arquitectura de red que se ha utilizado para ASR. Este modelo es adecuado si necesitas un modelo alternativo al QuartzNet para la transcripción en inglés.

stt_es_quartznet15x5: Este modelo es específico para español. Si tu audio está en español, este es el modelo que debes utilizar."""

# Configuración para convertir Audio a Texto (ASR)
asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_en_quartznet15x5") #5

# Configuración para convertir Texto a Audio (TTS)
tts_model = nemo_tts.models.Tacotron2Model.from_pretrained(model_name="tts_en_tacotron2") #6

# Check available WaveGlow models and select an appropriate one
print(nemo_tts.models.WaveGlowModel.list_available_models()) #7
# Example: Choose the first available model
vocoder_model_name = nemo_tts.models.WaveGlowModel.list_available_models()[0]
vocoder = nemo_tts.models.WaveGlowModel.from_pretrained(model_name="tts_en_waveglow_88m")

# Función para convertir audio a texto
def audio_to_text(audio_file):
    if audio_file.startswith('http'): # Handle URLs
        response = requests.get(audio_file)
        with open('temp_audio.wav', 'wb') as f:
            f.write(response.content)
        audio_file = 'temp_audio.wav' # Use the downloaded file

    # Cargar el audio
    audio, sample_rate = torchaudio.load(audio_file)
    # Asegurarse de que el audio esté en la frecuencia correcta
    if sample_rate != 16000:
        transform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        audio = transform(audio)

    # Realizar la transcripción
    # The transcribe method expects a list of file paths, not audio tensors.
    transcription = asr_model.transcribe([audio_file])
    return transcription[0]

# Función para convertir texto a audio
def text_to_audio(text, output_file="output.wav"):
    # Generar mel-spectrograma a partir del texto
    parsed = tts_model.parse(text)
    spectrogram = tts_model.generate_spectrogram(tokens=parsed)

    # Convertir mel-spectrograma a onda sonora
    audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)

    # Guardar el archivo de audio
    torchaudio.save(output_file, audio.to('cpu'), 22050)
    print(f"Audio saved to {output_file}")

from IPython.display import Audio

# Ejemplo de uso
audio_file = 'https://dldata-public.s3.us-east-2.amazonaws.com/2086-149220-0033.wav'
transcription = audio_to_text(audio_file)
print("Transcription:", transcription)

text = "This is a test of the text to speech conversion."
text_to_audio(text, output_file="output.wav")

# Reproduce el audio generado en Colab
Audio("output.wav", autoplay=True)
