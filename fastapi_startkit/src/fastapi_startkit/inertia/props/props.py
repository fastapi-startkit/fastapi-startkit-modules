class OptionalProp:
    def __init__(self, callback):
        self.callback = callback

    def __call__(self):
        return self.callback()
