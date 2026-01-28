"""
Text I/O for JarvisAI
Consolidated text input/output adapters
"""

from .input_adapter import CLIInput
from .output_adapter import TextOutput

__all__ = ["CLIInput", "TextOutput"]
