from typing import Any, List, Dict


class History:
    def __init__(self):
        self._states: List[Dict[str, Any]] = []
        self._current_idx: int = -1

    @property
    def length(self) -> int:
        return len(self._states)

    @property
    def state(self) -> Any:
        if 0 <= self._current_idx < len(self._states):
            return self._states[self._current_idx]["state"]
        return None

    def push_state(self, state: Any, title: str, url: str) -> None:
        if self._current_idx < len(self._states) - 1:
            self._states = self._states[:self._current_idx + 1]
        self._states.append({"state": state, "title": title, "url": url})
        self._current_idx += 1

    def replace_state(self, state: Any, title: str, url: str) -> None:
        if 0 <= self._current_idx < len(self._states):
            self._states[self._current_idx] = {"state": state, "title": title, "url": url}
        else:
            self.push_state(state, title, url)

    def back(self) -> None:
        if self._current_idx > 0:
            self._current_idx -= 1

    def forward(self) -> None:
        if self._current_idx < len(self._states) - 1:
            self._current_idx += 1


history = History()
