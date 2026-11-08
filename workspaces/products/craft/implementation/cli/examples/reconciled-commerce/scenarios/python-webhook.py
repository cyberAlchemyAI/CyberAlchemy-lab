from __future__ import annotations

import asyncio
import hashlib
import hmac
import importlib
import json
import pathlib
import re
import sys

target = pathlib.Path(sys.argv[1]).resolve()
route = sys.argv[2] if len(sys.argv) > 2 else "/webhook"
assert re.fullmatch(r"/[A-Za-z0-9/_-]+", route) and "//" not in route
source_root = target / "src"
sys.path.insert(0, str(source_root))

inbound_candidates = sorted(source_root.glob("**/providers/reference/inbound_http.py"))
assert len(inbound_candidates) == 1, f"expected one generated inbound provider, observed:{inbound_candidates}"
relative = inbound_candidates[0].relative_to(source_root)
package_parts = relative.parts[:-3]
assert package_parts and all(part.isidentifier() for part in package_parts), f"invalid generated package root:{package_parts}"
inbound_module = importlib.import_module(".".join((*package_parts, "providers", "reference", "inbound_http")))
create_webhook_application = inbound_module.create_webhook_application

BODY = b"domainspec-installed-webhook"
SECRET = "installed-reference-secret"
invocations = 0


async def on_webhook(body: bytes) -> None:
    global invocations
    assert body == BODY
    invocations += 1


application = create_webhook_application(SECRET, on_webhook)


async def serve_asgi(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        header_bytes = await reader.readuntil(b"\r\n\r\n")
        lines = header_bytes[:-4].split(b"\r\n")
        method, request_target, _version = lines[0].decode("ascii").split(" ", 2)
        headers = []
        content_length = 0
        for line in lines[1:]:
            name, value = line.split(b":", 1)
            normalized = (name.lower(), value.strip())
            headers.append(normalized)
            if normalized[0] == b"content-length":
                content_length = int(normalized[1])
        body = await reader.readexactly(content_length)
        sent = False

        async def receive():
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        status = 500
        response_headers = []
        response_body = bytearray()

        async def send(message):
            nonlocal status, response_headers
            if message["type"] == "http.response.start":
                status = message["status"]
                response_headers = list(message.get("headers", []))
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        path, _, query = request_target.partition("?")
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": query.encode("ascii"),
            "root_path": "",
            "headers": headers,
            "client": writer.get_extra_info("peername"),
            "server": writer.get_extra_info("sockname"),
        }
        await application(scope, receive, send)
        reason = {202: "Accepted", 401: "Unauthorized"}.get(status, "Response")
        response_headers.extend([(b"content-length", str(len(response_body)).encode("ascii")), (b"connection", b"close")])
        writer.write(f"HTTP/1.1 {status} {reason}\r\n".encode("ascii"))
        for name, value in response_headers:
            writer.write(name + b": " + value + b"\r\n")
        writer.write(b"\r\n" + response_body)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def request(port: int, signature: str) -> int:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(
        f"POST {route} HTTP/1.1\r\n".encode("ascii")
        + b"host: 127.0.0.1\r\n"
        + b"connection: close\r\n"
        + f"content-length: {len(BODY)}\r\n".encode("ascii")
        + f"x-domainspec-signature: {signature}\r\n\r\n".encode("ascii")
        + BODY
    )
    await writer.drain()
    status_line = await reader.readline()
    await reader.read()
    writer.close()
    await writer.wait_closed()
    return int(status_line.split(b" ", 2)[1])


async def main() -> None:
    server = await asyncio.start_server(serve_asgi, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    try:
        invalid_status = await request(port, "0" * 64)
        assert invalid_status == 401
        assert invocations == 0
        signature = hmac.new(SECRET.encode(), BODY, hashlib.sha256).hexdigest()
        valid_status = await request(port, signature)
        assert valid_status == 202
        assert invocations == 1
        print(json.dumps({"language": "python", "startup": "asgi-http-listener", "invalid_status": invalid_status, "valid_status": valid_status, "handler_invocations": invocations, "result": "pass"}, separators=(",", ":")))
    finally:
        server.close()
        await server.wait_closed()


asyncio.run(main())
