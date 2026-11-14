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






import logging
import signal
import threading

from django.core.management.base import BaseCommand

from mqtt.service import MQTTService


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start the MQTT service."

    def handle(self, *args, **options):
        mqtt_service = MQTTService()
        shutdown_event = threading.Event()

        def request_shutdown(signum, frame):
            logger.info(
                "Shutdown signal received: %s",
                signum,
            )
            shutdown_event.set()

        signal.signal(signal.SIGINT, request_shutdown)
        signal.signal(signal.SIGTERM, request_shutdown)

        self.stdout.write(
            self.style.SUCCESS("Starting MQTT service...")
        )

        try:
            mqtt_service.start()

            self.stdout.write(
                self.style.SUCCESS("MQTT service started.")
            )

            shutdown_event.wait()

        except KeyboardInterrupt:            
            
            self.stdout.write(
                self.style.WARNING(
                    "Stopping MQTT service..."
                )
            )

        except Exception:
            logger.exception(
                "MQTT worker stopped due to an unexpected error."
            )
            raise

        finally:
            mqtt_service.stop()

            self.stdout.write(
                self.style.WARNING("MQTT service stopped.")
            )
