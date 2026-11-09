import json
import logging
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from models import Command

log = logging.getLogger(__name__)


class CommandPublisher:
    def __init__(self, mqtt_url: str):
        url = urlparse(mqtt_url)
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="devices-service")
        self._client.connect_async(url.hostname, url.port or 1883)
        self._client.loop_start()

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def publish(self, command: Command) -> bool:
        result = self._client.publish(
            f'devices/{command.device_id}/commands', 
            payload = command.model_dump_json(), 
            qos = 1
        )
        return result.rc == mqtt.MQTT_ERR_SUCCESS
