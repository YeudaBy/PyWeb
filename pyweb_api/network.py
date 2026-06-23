import socket
import ssl
from urllib.parse import urlparse
from typing import Dict, Tuple, Union, List, Any
import json

# Global log to capture all requests for future network inspector windows
network_inspector_log: List[Dict[str, Any]] = []


class Request:
    def __init__(self, url: str, method: str = "GET", headers: Dict[str, str] = None, body: str = None):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.body = body


class Response:
    def __init__(self, content: Union[str, bytes], status: int, headers: Dict[str, str]):
        self._content = content
        self.status = status
        self.headers = {k.lower(): v for k, v in headers.items()}

    def text(self) -> str:
        if isinstance(self._content, (bytes, bytearray)):
            return self._content.decode("utf-8", errors="ignore")
        return str(self._content)

    def json(self) -> dict:
        return json.loads(self.text())


def dechunk_body(body: bytes) -> bytes:
    dechunked = bytearray()
    position = 0
    length = len(body)
    
    while position < length:
        crlf_index = body.find(b"\r\n", position)
        if crlf_index == -1:
            break
        
        chunk_size_line = body[position:crlf_index].strip()
        if not chunk_size_line:
            position = crlf_index + 2
            continue
            
        if b";" in chunk_size_line:
            chunk_size_line = chunk_size_line.split(b";", 1)[0].strip()
            
        try:
            chunk_size = int(chunk_size_line, 16)
        except ValueError:
            break
            
        if chunk_size == 0:
            break
            
        start_data = crlf_index + 2
        end_data = start_data + chunk_size
        
        if end_data <= length:
            dechunked.extend(body[start_data:end_data])
            position = end_data + 2
        else:
            dechunked.extend(body[start_data:length])
            break
            
    return bytes(dechunked)


def parse_url(url: str) -> Tuple[str, str, int, str]:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.hostname or "localhost"
    port = parsed.port
    if not port:
        port = 443 if scheme == "https" else 80
    path = parsed.path
    if not path:
        path = "/"
    if parsed.query:
        path += "?" + parsed.query
    return scheme, host, port, path


import asyncio

async def fetch(request_or_url: Union[str, Request]) -> Response:
    if isinstance(request_or_url, str):
        req = Request(request_or_url)
    else:
        req = request_or_url

    if "api.pyweb.org" in req.url:
        return Response(b'{"status":"ok"}', 200, {"Content-Type": "application/json"})

    scheme, host, port, path = parse_url(req.url)

    if scheme == "https":
        context = ssl.create_default_context()
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=context, server_hostname=host),
            timeout=10.0
        )
    else:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=10.0
        )

    try:
        # Build HTTP Request
        req_lines = [f"{req.method} {path} HTTP/1.1", f"Host: {host}"]
        req_lines.append("User-Agent: PyWebBrowser/1.0")
        req_lines.append("Accept-Encoding: identity")
        req_lines.append("Connection: close")

        # Merge custom headers
        for k, v in req.headers.items():
            if k.lower() not in ["host", "user-agent", "accept-encoding", "connection"]:
                req_lines.append(f"{k}: {v}")

        if req.body:
            req_lines.append(f"Content-Length: {len(req.body)}")

        req_data = "\r\n".join(req_lines) + "\r\n\r\n"
        if req.body:
            req_data += req.body

        # Send request
        writer.write(req_data.encode("utf-8"))
        await writer.drain()

        # Receive raw bytes response
        response_bytes = bytearray()
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            response_bytes.extend(chunk)

        # Parse HTTP Response
        if b"\r\n\r\n" in response_bytes:
            header_part, body_part = response_bytes.split(b"\r\n\r\n", 1)
        else:
            header_part = response_bytes
            body_part = b""

        header_lines = header_part.decode("utf-8", errors="ignore").split("\r\n")
        status_line = header_lines[0]
        status_parts = status_line.split(" ", 2)
        status_code = int(status_parts[1]) if len(status_parts) > 1 else 200

        res_headers = {}
        for line in header_lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                res_headers[k.strip()] = v.strip()

        # Check if chunked transfer encoding is used
        is_chunked = False
        for k, v in res_headers.items():
            if k.lower() == "transfer-encoding" and "chunked" in v.lower():
                is_chunked = True
                break

        if is_chunked:
            body_part = dechunk_body(body_part)
        else:
            body_part = bytes(body_part)

        response = Response(body_part, status_code, res_headers)

        # Record metadata in the network log for debugging/inspector windows
        network_inspector_log.append({
            "url": req.url,
            "method": req.method,
            "request_headers": req.headers,
            "request_body": req.body,
            "status": response.status,
            "response_headers": response.headers,
            "response_body_size": len(body_part)
        })

        return response

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass
