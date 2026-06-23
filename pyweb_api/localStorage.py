from typing import Optional


class LocalStorage:
    def __init__(self):
        self._data = {}

    def get_item(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set_item(self, key: str, value: str) -> None:
        self._data[key] = str(value)

    def remove_item(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        self._data.clear()


localStorage = LocalStorage()
