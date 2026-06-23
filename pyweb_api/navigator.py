class Navigator:
    @property
    def user_agent(self) -> str:
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PyWebBrowser/1.0"

    @property
    def language(self) -> str:
        return "he-IL"

    @property
    def on_line(self) -> bool:
        return True


navigator = Navigator()
