"""Tapo P100 interactions"""
import asyncio
import base64
import hashlib
import json
import logging
import time
from base64 import b64decode
from typing import Optional, Union

import aiohttp
import pkcs7
from aiohttp.client_reqrep import ClientResponse
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

from .device_info import DeviceInfo

_LOGGER = logging.getLogger(__name__)


class P100:
    """Tapo P100 representation"""

    def __init__(
        self,
        address: str,
        email: str,
        password: str,
        session: aiohttp.ClientSession,
    ):
        self.address = address
        self.email = b64_encode(sha1(email))
        self.password = b64_encode(password)
        self.rsa_key = RSA.generate(1024)
        self.session = session
        self.aes_key_iv: Optional[bytes] = None
        self.token: Optional[str] = None

    def __repr__(self):
        return f"P100({self.address})"

    async def turn_on(self):
        """Send `turn on` request to device"""
        await self.send_encrypted_request("set_device_info", {"device_on": True})

    async def turn_off(self):
        """Send `turn off` request to device"""
        await self.send_encrypted_request("set_device_info", {"device_on": False})

    async def device_info(self):
        """Request `DeviceInfo` from device"""
        info = await self.send_encrypted_request("get_device_info")
        _LOGGER.debug(info)
        info["nickname"] = b64decode(info["nickname"]).decode("utf-8")
        info["ssid"] = b64decode(info["ssid"]).decode("utf-8")
        return DeviceInfo(**info)

    async def turn_on_led(self):
        """Send `turn on led` request to device"""
        await self.send_encrypted_request("set_led_info", {"led_rule": "always"})

    async def turn_off_led(self):
        """Send `turn off led` request to device"""
        await self.send_encrypted_request("set_led_info", {"led_rule": "never"})

    async def device_led_info(self):
        """Request led info from device"""
        return await self.send_encrypted_request("get_led_info")

    def send_encrypted_request(self, method: str, params=None):
        """Send raw `securePassthrough` request to device"""
        try:
            return self._send_encrypted_request(method, params)
        except ValueError as exception:
            _LOGGER.info(f"Got {exception=!r}, trying handshake again")
            self.handshake()
            return self._send_encrypted_request(method, params)

    async def _send_encrypted_request(self, method: str, params=None) -> dict:
        params = {
            "method": method,
            "params": params,
            "requestTimeMils": int(round(time.time() * 1000)),
        }
        request = await self.encrypt(params)
        result = await self.send_request("securePassthrough", {"request": request})
        response = json.loads(await self.decrypt(result["response"]))
        check_error(response)
        return response.get("result")

    async def send_request(self, method: str, params) -> dict:
        """Send raw request to device"""
        url = f"http://{self.address}/app"
        data = {
            "method": method,
            "params": {
                **params,
                "requestTimeMils": int(round(time.time() * 1000)),
            },
        }
        query_params = {"token": self.token} if self.token else None
        # the plug may be unavailable for couple of ms after discovery
        # add some delay if you facing server disconnect errors
        async with self.session.post(url, json=data, params=query_params) as response:
            self.set_cookies(response)
            response_data = await response.json()
            # have no idea why, but it prevents
            # ConnectionResetError: Cannot write to closing transport
            await asyncio.sleep(0)
        check_error(response_data)
        return response_data.get("result")

    def set_cookies(self, response: ClientResponse):
        """Set proper session cookies"""
        # because the TP-Link can't read the fucking rfc6265
        if cookie := response.cookies.get("TP_SESSIONID"):
            self.session.cookie_jar.clear()
            self.session.cookie_jar.update_cookies({cookie.key: cookie.value})

    async def encrypt(self, data):
        """Encrypt `data` with TP-Link encryption method"""
        data = pkcs7.PKCS7Encoder().encode(json.dumps(data))
        cipher = await self.cipher()
        encrypted = cipher.encrypt(data.encode("utf-8"))
        return b64_encode(encrypted)

    async def decrypt(self, text: str):
        """Decrypt `data` with TP-Link encryption method"""
        data = base64.b64decode(text.encode("utf-8"))
        cipher = await self.cipher()
        decrypted = cipher.decrypt(data).decode("utf-8")
        return pkcs7.PKCS7Encoder().decode(decrypted)

    async def handshake(self):
        """Send `handshake` request to device.
        This method calls `login_device` automatically.
        """
        self.reset_session()
        public_key = self.rsa_key.public_key().export_key().decode()
        result = await self.send_request("handshake", {"key": public_key})
        encrypted_key = b64decode(result["key"].encode("utf-8"))
        cipher = PKCS1_v1_5.new(self.rsa_key)
        self.aes_key_iv = cipher.decrypt(encrypted_key, None)

        await self.login_device()

    def reset_session(self):
        """Clear `session.cookie_jar` and `token`"""
        self.token = None
        self.session.cookie_jar.clear()

    async def login_device(self):
        """Send `login_device` request to device"""
        result = await self.send_encrypted_request(
            "login_device",
            {
                "username": self.email,
                "password": self.password,
            },
        )

        self.token = result["token"]

    async def cipher(self):
        """Prepare AES cipher.
        This method calls `handshake` automatically when no AES key loaded.
        """
        if not self.aes_key_iv:
            await self.handshake()

        return AES.new(
            key=self.aes_key_iv[:0x10],
            mode=AES.MODE_CBC,
            iv=self.aes_key_iv[0x10:0x20],
        )


def check_error(response):
    """Assert `error_code == 0`"""
    if (error_code := response["error_code"]) != 0:
        raise ValueError(f"{error_code=}")


def b64_encode(data: Union[bytes, str]):
    """Base64 encode"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def sha1(data: str):
    """SHA1 digest"""
    return hashlib.sha1(data.encode("utf-8")).hexdigest()
