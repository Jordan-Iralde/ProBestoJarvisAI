"""
Consolidated I/O Module for JarvisAI v0.0.4
Handles all input/output operations: CLI, voice, text
"""

# CLI Interface
from .cli.interface import AdvancedCLI, Colors

# Text I/O
from .text.input_adapter import CLIInput
from .text.output_adapter import TextOutput

# Voice I/O
from .voice.stt import VoskSTT
from .voice.tts import TTS

# Voice Pipeline
from .voice_pipeline import VoiceIOPipeline

__all__ = [
    "AdvancedCLI",
    "Colors",
    "CLIInput",
    "TextOutput",
    "VoskSTT",
    "TTS",
    "VoiceIOPipeline",
]
