class Module:
    def __init__(self):
        self.name = "example_module"

    def on_load(self):
        print("[example_module] cargado correctamente.")

    def run(self, input_data):
        return f"[example_module] respuesta a: {input_data}"
