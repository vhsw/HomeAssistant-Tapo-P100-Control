import base64
import hashlib
import json
import time
from base64 import b64decode
from typing import Optional, Union

import pkcs7
import requests
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

from .device_info import DeviceInfo


class P100:
    def __init__(self, address: str, email: str, password: str):
        self.address = address
        self.email = b64_encode(sha1(email))
        self.password = b64_encode(password)
        self.rsa_key = RSA.generate(1024)
        self.session = requests.session()
        self.aes_key_iv: Optional[bytes] = None
        self.token: Optional[str] = None

    def __repr__(self):
        return f"P100({self.address})"

    def turn_on(self):
        self.send_encrypted_request("set_device_info", {"device_on": True})

    def turn_off(self):
        self.send_encrypted_request("set_device_info", {"device_on": False})

    def device_info(self):
        info = self.send_encrypted_request("get_device_info")
        info["nickname"] = b64decode(info["nickname"]).decode("utf-8")
        info["ssid"] = b64decode(info["ssid"]).decode("utf-8")
        return DeviceInfo(**info)

    def send_encrypted_request(self, method: str, params=None):
        try:
            return self._send_encrypted_request(method, params)
        except ValueError:
            self.handshake()
            return self._send_encrypted_request(method, params)

    def _send_encrypted_request(self, method: str, params=None):
        params = {
            "method": method,
            "params": params,
            "requestTimeMils": int(round(time.time() * 1000)),
        }
        request = self.encrypt(params)
        result = self.send_request("securePassthrough", {"request": request})
        response = json.loads(self.decrypt(result["response"]))
        check_error(response)
        return response.get("result")

    def send_request(self, method: str, params):
        url = f"http://{self.address}/app"
        data = {
            "method": method,
            "params": {
                **params,
                "requestTimeMils": int(round(time.time() * 1000)),
            },
        }
        query_params = {"token": self.token} if self.token else None
        response = self.session.post(url, json=data, params=query_params).json()
        check_error(response)
        return response.get("result")

    def encrypt(self, data):
        data = pkcs7.PKCS7Encoder().encode(json.dumps(data))
        encrypted = self.cipher.encrypt(data.encode("utf-8"))
        return b64_encode(encrypted)

    def decrypt(self, text: str):
        data = base64.b64decode(text.encode("utf-8"))
        decrypted = self.cipher.decrypt(data).decode("utf-8")
        return pkcs7.PKCS7Encoder().decode(decrypted)

    def handshake(self):
        self.reset_session()
        public_key = self.rsa_key.public_key().export_key("PEM").decode("utf-8")
        result = self.send_request("handshake", {"key": public_key})
        encrypted_key = b64decode(result["key"].encode("utf-8"))
        cipher = PKCS1_v1_5.new(self.rsa_key)
        self.aes_key_iv = cipher.decrypt(encrypted_key, None)
        self.login_device()

    def reset_session(self):
        self.token = None
        self.session.cookies.clear_session_cookies()

    def login_device(self):
        result = self.send_encrypted_request(
            "login_device",
            {
                "username": self.email,
                "password": self.password,
            },
        )
        self.token = result["token"]

    @property
    def cipher(self):
        if not self.aes_key_iv:
            self.handshake()

        return AES.new(
            key=self.aes_key_iv[:0x10],
            mode=AES.MODE_CBC,
            iv=self.aes_key_iv[0x10:0x20],
        )


def check_error(response):
    if error_code := response["error_code"] != 0:
        raise ValueError(f"{error_code=}")


def b64_encode(data: Union[bytes, str]):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def sha1(data: str):
    return hashlib.sha1(data.encode("utf-8")).hexdigest()
