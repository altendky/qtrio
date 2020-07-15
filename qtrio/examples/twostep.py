class TwoStep:
    def __init__(self, a_signal, some_path):
        self.signal = a_signal
        self.file = None
        self.some_path = some_path

    def before(self):
        self.file = open(some_path, 'w')
        self.signal.connect(self.after)
        self.file.write('before')

    def after(self, value):
        self.signal.disconnect(self.after)
        self.file.write(f'after {value!r}')
        self.file.close()
        
