# core/lifecycle/runtime/io.py
class IOChannel:
    def __init__(self, state):
        self.state = state

    def send_input(self, text):
        self.state.push_event({"type": "input.text", "data": text})
