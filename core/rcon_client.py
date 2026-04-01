"""
Source Engine RCON protocol client.
https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
"""
from __future__ import annotations
import socket
import struct
import threading
from typing import Optional


SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0


class RconError(Exception):
    pass


class RconClient:
    def __init__(self):
        self._sock: Optional[socket.socket] = None
        self._lock = threading.Lock()
        self._req_id = 0
        self.connected = False

    def connect(self, host: str, port: int, password: str, timeout: float = 5.0) -> None:
        """Connect and authenticate. Raises RconError on failure."""
        self.disconnect()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, int(port)))
            self._sock = sock
        except OSError as e:
            raise RconError(f"Cannot connect to {host}:{port} - {e}") from e

        # Authenticate
        req_id = self._next_id()
        self._send_packet(req_id, SERVERDATA_AUTH, password)
        pkt = self._recv_packet()
        if pkt is None:
            raise RconError("No response to auth packet")
        # Auth response: request_id == -1 means bad password
        if pkt[0] == -1:
            self._sock.close()
            self._sock = None
            raise RconError("RCON authentication failed - check password")
        self.connected = True

    def send_command(self, command: str) -> str:
        """Send an RCON command and return the response string."""
        if not self.connected or self._sock is None:
            raise RconError("Not connected")
        with self._lock:
            req_id = self._next_id()
            self._send_packet(req_id, SERVERDATA_EXECCOMMAND, command)
            # Send a follow-up empty request to detect end of multi-packet response
            term_id = self._next_id()
            self._send_packet(term_id, SERVERDATA_EXECCOMMAND, "")

            response_parts = []
            while True:
                pkt = self._recv_packet()
                if pkt is None:
                    break
                pid, ptype, body = pkt
                if pid == term_id:
                    break
                if ptype == SERVERDATA_RESPONSE_VALUE and pid == req_id:
                    response_parts.append(body)
            return "".join(response_parts)

    def disconnect(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self.connected = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_id(self) -> int:
        self._req_id = (self._req_id % 10000) + 1
        return self._req_id

    def _send_packet(self, request_id: int, packet_type: int, body: str) -> None:
        body_bytes = body.encode("utf-8") + b"\x00\x00"
        size = 4 + 4 + len(body_bytes)
        packet = struct.pack("<iii", size, request_id, packet_type) + body_bytes
        self._sock.sendall(packet)

    def _recv_packet(self) -> Optional[tuple[int, int, str]]:
        try:
            raw_size = self._recvall(4)
            if not raw_size:
                return None
            size = struct.unpack("<i", raw_size)[0]
            data = self._recvall(size)
            if len(data) < 8:
                return None
            request_id, packet_type = struct.unpack("<ii", data[:8])
            body = data[8:].rstrip(b"\x00").decode("utf-8", errors="replace")
            return request_id, packet_type, body
        except (OSError, struct.error):
            return None

    def _recvall(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                return buf
            buf += chunk
        return buf
