class Location:
    def __init__(self, on_location_change):
        self.history = []
        self.current_index = -1
        self._current_url = None
        self.on_location_change = on_location_change

    @property
    def href(self):
        return self._current_url

    def navigate(self, url: str):
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        self.history.append(url)
        self.current_index += 1
        self._current_url = url
        self.on_location_change(url)

    def back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._current_url = self.history[self.current_index]
            self.on_location_change(self._current_url)
            return self._current_url
        self.on_location_change(None)
        return None

    def forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self._current_url = self.history[self.current_index]
            self.on_location_change(self._current_url)
            return self._current_url
        self.on_location_change(None)
        return None

    def clear_history(self):
        self.history.clear()
        self.current_index = -1

    def reload(self):
        self.navigate(self._current_url)



