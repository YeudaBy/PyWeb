class Event:
    def __init__(self, type_, target):
        self.type = type_
        self.target = target
        self.current_target = None
        self._stopped = False
        self.default_prevented = False

    def stop_propagation(self):
        self._stopped = True

    def prevent_default(self):
        self.default_prevented = True

    def preventDefault(self):
        self.prevent_default()


