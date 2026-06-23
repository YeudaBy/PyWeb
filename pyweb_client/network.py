from io import BytesIO
from typing import Union
from pyweb_api.network import fetch, Request


async def fetch_text(url_or_request: Union[str, Request]) -> str:
    res = await fetch(url_or_request)
    if res.status >= 400:
        raise Exception(f"HTTP Error: {res.status}")
    return res.text()


async def fetch_binary(url: str) -> BytesIO:
    res = await fetch(url)
    if res.status >= 400:
        raise Exception(f"HTTP Error: {res.status}")
    content = res._content
    if isinstance(content, str):
        content = content.encode("utf-8")
    return BytesIO(content)
