"""
dfs_client.py — TCP client for the Go distributed file storage core.

Every call opens a TCP connection, sends a JSON request, reads the JSON
response, and closes the connection. Stateless and thread-safe.
"""

import json
import socket
import base64
from typing import Optional


class DFSError(Exception):
    pass


class DFSClient:
    """Talks to one Go DFS node over TCP."""

    TIMEOUT = 15  # seconds

    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        self.host = host
        self.port = port

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def ping(self) -> bool:
        try:
            resp = self._send({"type": "PING"})
            return resp.get("ok", False)
        except Exception:
            return False

    def store(self, key: str, data: bytes) -> str:
        """Upload *data* to the node.  Returns the stored key."""
        resp = self._send({
            "type": "STORE",
            "key": key,
            "data": base64.b64encode(data).decode(),
        })
        if not resp.get("ok"):
            raise DFSError(resp.get("error", "store failed"))
        return resp["key"]

    def retrieve(self, key: str) -> bytes:
        """Download and return the decrypted file bytes for *key*."""
        resp = self._send({"type": "RETRIEVE", "key": key})
        if not resp.get("ok"):
            raise DFSError(resp.get("error", "retrieve failed"))
        return base64.b64decode(resp["data"])

    def delete(self, key: str) -> None:
        resp = self._send({"type": "DELETE", "key": key})
        if not resp.get("ok"):
            raise DFSError(resp.get("error", "delete failed"))

    def list_files(self) -> list[str]:
        resp = self._send({"type": "LIST"})
        if not resp.get("ok"):
            raise DFSError(resp.get("error", "list failed"))
        return resp.get("keys") or []

    def peers(self) -> list[dict]:
        resp = self._send({"type": "PEERS"})
        if not resp.get("ok"):
            raise DFSError(resp.get("error", "peers failed"))
        return resp.get("peers") or []

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _send(self, payload: dict) -> dict:
        raw = (json.dumps(payload) + "\n").encode()
        with socket.create_connection((self.host, self.port), timeout=self.TIMEOUT) as sock:
            sock.sendall(raw)
            # Read until the connection closes (Go closes after responding)
            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        return json.loads(b"".join(chunks).decode().strip())

    def __repr__(self):
        return f"DFSClient({self.host}:{self.port})"
