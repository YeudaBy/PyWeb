class Location:
    def __init__(self, on_location_change):
        self.history = []
        self.current_index = -1
        self._current_url = None
        self._current_request = None
        self.on_location_change = on_location_change

    @property
    def href(self):
        return self._current_url

    def navigate(self, url_or_request):
        from pyweb_api.network import Request
        if isinstance(url_or_request, Request):
            url = url_or_request.url
            self._current_request = url_or_request
        else:
            url = url_or_request
            self._current_request = None

        if "://" not in url:
            from urllib.parse import urljoin
            if self._current_url:
                url = urljoin(self._current_url, url)
                if isinstance(url_or_request, Request):
                    url_or_request.url = url
                else:
                    url_or_request = url

        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        self.history.append(url)
        self.current_index += 1
        self._current_url = url
        self.on_location_change(url_or_request)

    def back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._current_url = self.history[self.current_index]
            self._current_request = None
            self.on_location_change(self._current_url)
            return self._current_url
        return None

    def forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self._current_url = self.history[self.current_index]
            self._current_request = None
            self.on_location_change(self._current_url)
            return self._current_url
        return None

    def clear_history(self):
        self.history.clear()
        self.current_index = -1

    def reload(self):
        self.navigate(self._current_request or self._current_url)



