class Event:
    def __init__(self, type_, target):
        self.type = type_
        self.target = target
        self.current_target = None
        self._stopped = False

    def stop_propagation(self):
        self._stopped = True

