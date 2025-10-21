import io

class QTextEditLogger(io.StringIO):
    def __init__(self, log_window):
        super().__init__()
        self.log_window = log_window

    def write(self, text):
        """Emit text to the log window via signal."""
        text = text.strip()
        if text:
            self.log_window.emitter.log_signal.emit(text)

    def flush(self):
        """Required for file-like compatibility (does nothing here)."""
        pass