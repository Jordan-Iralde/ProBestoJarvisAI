from tensorflow.keras.callbacks import Callback
from tqdm import tqdm

class TqdmCallback(Callback):
    def _init_(self, verbose=1):
        super()._init_()
        self.verbose = verbose

    def on_epoch_end(self, epoch, logs=None):
        if self.verbose:
            tqdm.write(f"Epoch {epoch + 1} - loss: {logs['loss']:.4f} - accuracy: {logs['accuracy']:.4f}")