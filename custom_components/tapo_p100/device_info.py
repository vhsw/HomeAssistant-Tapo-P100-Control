"""Device info wrapper module"""
from dataclasses import dataclass


@dataclass
class DeviceInfo:  # pylint: disable=too-many-instance-attributes
    """Device info wrapper"""

    device_id: str = ""
    fw_ver: str = ""
    hw_ver: str = ""
    type: str = ""
    model: str = ""
    mac: str = ""
    hw_id: str = ""
    fw_id: str = ""
    oem_id: str = ""
    specs: str = ""
    device_on: bool = False
    on_time: int = 0
    overheated: bool = False
    nickname: str = ""
    location: str = ""
    avatar: str = "plug"
    longitude: int = 0
    latitude: int = 0
    has_set_location_info: bool = False
    ip: str = ""  # pylint: disable=invalid-name
    ssid: str = ""
    signal_level: int = 0
    rssi: int = 0
    region: str = ""
    time_diff: int = 0
    lang: str = "en_EN"
    default_states: str = ""
