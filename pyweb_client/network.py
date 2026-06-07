from io import BytesIO

import requests


def fetch_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def fetch_binary(url: str) -> BytesIO:
    u = requests.get(url)
    return BytesIO(u.content)
