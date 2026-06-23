from io import BytesIO
from pyweb_api.network import fetch


def fetch_text(url: str) -> str:
    res = fetch(url)
    if res.status >= 400:
        raise Exception(f"HTTP Error: {res.status}")
    return res.text()


def fetch_binary(url: str) -> BytesIO:
    res = fetch(url)
    if res.status >= 400:
        raise Exception(f"HTTP Error: {res.status}")
    content = res._content
    if isinstance(content, str):
        content = content.encode("utf-8")
    return BytesIO(content)
