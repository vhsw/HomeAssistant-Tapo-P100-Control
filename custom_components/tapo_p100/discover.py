"""Implementation of TP-Link Device Discovery Protocol"""

import binascii
import json
import socket
from random import randbytes

BROADCAST = "255.255.255.255"


def discover():
    """Get `device_id` and `ip`"""
    try:
        result = send_request()
        return {
            "device_id": result["device_id"],
            "ip": result["ip"],
        }
    except socket.timeout as exc:
        raise TimeoutError from exc


def send_request() -> dict:
    """Send discovery UDP request"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    message = build_message()
    sock.sendto(message, (BROADCAST, 20002))
    data, _ = sock.recvfrom(1024)
    return json.loads(data[0x10:].decode())["result"]


def build_message():
    """Build discovery message"""

    header = bytes.fromhex("0200000101e51100")
    magic_const = 0x5A6B7C8D .to_bytes(4, "big")
    random = randbytes(4)
    request = header + random + magic_const
    crc = binascii.crc32(request).to_bytes(4, "big")
    return request[:12] + crc + request[16:]
