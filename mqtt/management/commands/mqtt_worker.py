# import logging
# import threading

# from django.core.management.base import BaseCommand

# from mqtt.service import MQTTService


# logger = logging.getLogger(__name__)


# class Command(BaseCommand):
#     help = "Start the MQTT service."

#     def handle(self, *args, **options):
#         mqtt_service = MQTTService()
#         shutdown_event = threading.Event()

#         self.stdout.write(
#             self.style.SUCCESS("Starting MQTT service...")
#         )

#         try:
#             mqtt_service.start()

#             self.stdout.write(
#                 self.style.SUCCESS(
#                     "MQTT service is running."
#                 )
#             )

#             shutdown_event.wait()

#         except KeyboardInterrupt:
#             self.stdout.write(
#                 self.style.WARNING(
#                     "Stopping MQTT service..."
#                 )
#             )

#         except Exception:
#             logger.exception(
#                 "MQTT service stopped because of an unexpected error."
#             )

#         finally:
#             mqtt_service.stop()






# import logging
# import signal
# import threading

# from django.core.management.base import BaseCommand

# from mqtt.service import MQTTService


# logger = logging.getLogger(__name__)


# class Command(BaseCommand):
#     help = "Start the MQTT service."

#     def handle(self, *args, **options):
#         mqtt_service = MQTTService()
#         shutdown_event = threading.Event()

#         def request_shutdown(signum, frame):
#             logger.info(
#                 "Shutdown signal received: %s",
#                 signum,
#             )
#             shutdown_event.set()

#         signal.signal(signal.SIGINT, request_shutdown)
#         signal.signal(signal.SIGTERM, request_shutdown)

#         self.stdout.write(
#             self.style.SUCCESS("Starting MQTT service...")
#         )

#         try:
#             mqtt_service.start()

#             self.stdout.write(
#                 self.style.SUCCESS("MQTT service started.")
#             )

#             shutdown_event.wait()

#         except Exception:
#             logger.exception(
#                 "MQTT worker stopped due to an unexpected error."
#             )
#             raise

#         finally:
#             mqtt_service.stop()

#             self.stdout.write(
#                 self.style.WARNING("MQTT service stopped.")
#             )






import json
import logging
import signal
import threading

from django.core.management.base import BaseCommand

from mqtt.service import MQTTService
from mqtt.redis_bus import RedisBus


logger = logging.getLogger(__name__)

REDIS_COMMAND_CHANNEL = "iocl:mqtt:commands"


class Command(BaseCommand):
    help = "Start the MQTT service."

    def handle(self, *args, **options):
        mqtt_service = MQTTService()
        redis_bus = RedisBus()

        shutdown_event = threading.Event()
        pubsub = None
        redis_thread = None

        def request_shutdown(signum, frame):
            logger.info("Shutdown signal received: %s", signum)
            shutdown_event.set()

        def process_redis_messages():
            try:
                for message in pubsub.listen():

                    if shutdown_event.is_set():
                        break

                    if message["type"] != "message":
                        continue

                    try:
                        command = json.loads(message["data"])

                        topic = command["topic"]
                        payload = command["payload"]
                        qos = command.get("qos", 1)

                        if not isinstance(topic, str) or not topic.strip():
                            raise ValueError("Invalid MQTT topic.")

                        if not isinstance(payload, str):
                            raise ValueError("MQTT payload must be text.")

                        if qos not in (0, 1, 2):
                            raise ValueError("Invalid MQTT QoS.")

                        if not mqtt_service.is_connected:
                            raise ConnectionError(
                                "MQTT broker is not connected."
                            )

                        result = mqtt_service.publisher.publish(
                            topic=topic,
                            payload=payload,
                            qos=qos,
                        )

                        result.wait_for_publish(timeout=10)

                        if not result.is_published():
                            raise TimeoutError(
                                "MQTT publish acknowledgement timed out."
                            )

                        logger.info(
                            "MQTT message published. Topic: %s, Payload: %s",
                            topic,
                            payload,
                        )

                    except Exception:
                        logger.exception(
                            "Failed to process Redis MQTT command."
                        )

            except Exception:
                if not shutdown_event.is_set():
                    logger.exception(
                        "Redis command listener stopped unexpectedly."
                    )

        signal.signal(signal.SIGINT, request_shutdown)
        signal.signal(signal.SIGTERM, request_shutdown)

        self.stdout.write(
            self.style.SUCCESS("Starting MQTT service...")
        )

        try:
            # Start the existing MQTT connection.
            mqtt_service.start()

            # Subscribe to Redis command channel.
            pubsub = redis_bus.subscribe(REDIS_COMMAND_CHANNEL)

            # Start Redis listener thread.
            redis_thread = threading.Thread(
                target=process_redis_messages,
                daemon=True,
                name="redis-mqtt-listener",
            )
            redis_thread.start()

            self.stdout.write(
                self.style.SUCCESS(
                    "MQTT service and Redis command listener started."
                )
            )

            shutdown_event.wait()

        except Exception:
            logger.exception(
                "MQTT worker stopped due to an unexpected error."
            )
            raise

        finally:
            shutdown_event.set()

            if pubsub:
                pubsub.close()

            if redis_thread:
                redis_thread.join(timeout=5)

            redis_bus.close()
            mqtt_service.stop()

            self.stdout.write(
                self.style.WARNING("MQTT worker stopped.")
            )