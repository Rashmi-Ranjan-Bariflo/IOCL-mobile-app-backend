import logging

from .client import MQTTClient


logger = logging.getLogger(__name__)


class MQTTService:
    def __init__(self):
        self.client = MQTTClient()
        self._started = False

    def start(self):
        if self._started:
            logger.warning("MQTT service is already running.")
            return

        self.client.connect()
        self._started = True

        logger.info("MQTT service started successfully.")

    def stop(self):
        if not self._started:
            return

        self.client.disconnect()
        self._started = False

        logger.info("MQTT service stopped successfully.")

    @property
    def is_running(self):
        return self._started