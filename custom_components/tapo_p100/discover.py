"""Imlpementation of TP-Link Device Discovery Protocol"""
# pylint: disable=logging-fstring-interpolation

import json
import logging
import socket

_LOGGER = logging.getLogger(__name__)


HEADER = b"\x02\x00\x00\x01\x01\xe5\x11\x00\x07\x01\xae\xde\xc3nU\x1f"
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyQ9aL1SlIAr8XBEzj579
shdmwUc1qDmPVLqPheHEHWqqdvF6fQt0FMG8Ig117+29yHxuKfBhs5K+3ouxkwTc
+2V35rpKBplC0DRQvnL8P1rzSfdeeErhzpVryVtlo332qX9cqyszyT0HXISDK8mq
S5gSYbmNAoh/Yqo82F55VkdAPeagsTE2m+9FyG3Lz0CI4NCbIkKmMI3Yi9G0eTRr
6ehLMvFYTzVZq96ykwTqd613WdWEhSebiFKccjnQdHOzTkCwDGK3K+V0WkkEGgLw
JLGKk9oyFoVqkWfxztclVX6+FODeIZZ2QXA760Bg6q38+JS6tikl88RIMO7uvDGL
IwIDAQAB
-----END PUBLIC KEY-----
"""


def discover():
    """Get device IP and ID"""
    result = send_request()["result"]
    if result["device_type"] == "SMART.TAPOPLUG":
        return {
            "device_id": result["device_id"],
            "ip": result["ip"],
        }
    return {}


def send_request() -> dict:
    """Send discovery UDP request"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    body = {"params": {"rsa_key": PUBLIC_KEY}}
    message = HEADER + json.dumps(body, separators=(",", ":")).encode()

    _LOGGER.debug(f"tx: {message!r}")
    sock.sendto(message, ("255.255.255.255", 20002))

    data, addr = sock.recvfrom(1024)
    _LOGGER.debug(f"rx: {data!r}, {addr=}")

    return json.loads(data[0x10:].decode())
