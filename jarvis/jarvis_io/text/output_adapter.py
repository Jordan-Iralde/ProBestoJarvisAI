# io/text/output_adapter.py
"""Text output adapter for CLI"""


class TextOutput:
    """Simple text output to stdout"""

    def __init__(self, logger=None):
        self.logger = logger

    def send(self, text: str):
        """Send text to stdout"""
        if text is None:
            return
        print(text)

    def send_formatted(self, text: str, style: str = "default"):
        """Send formatted text"""
        styles = {
            "default": text,
            "success": f"✅ {text}",
            "error": f"❌ {text}",
            "warning": f"⚠️  {text}",
            "info": f"ℹ️  {text}",
        }
        output = styles.get(style, text)
        self.send(output)
