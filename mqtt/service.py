import logging
import json

from .client import MQTTClient
from .publisher import MQTTPublisher
from .subscriber import MQTTSubscriber
from .topics import MQTT_SUBSCRIPTION_TOPICS
import json
from django.utils import timezone
from django.db import transaction

<<<<<<< HEAD
from .topics import (
    MQTT_VALVE_ACK_TOPIC,
    MQTT_VALVE_STATUS_TOPIC,
    MQTT_SUBSCRIPTION_TOPICS,
    DEVICE_STATUS,
=======
from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchEventLog,
    StageBatchEquipmentExecution,
    StageEquipmentConfig
>>>>>>> 5a99b87 (status api reponse changed)
)

logger = logging.getLogger(__name__)


class MQTTService:

    def __init__(self):
        self.client = MQTTClient()
        self._started = False

        self.publisher = MQTTPublisher(self.client)
        self.subscriber = MQTTSubscriber(self.client)
<<<<<<< HEAD

        self.subscriber.set_message_handler(self._handle_message)
=======
        self.subscriber.set_message_handler(
            self._handle_message
        )
>>>>>>> fbbd939aa1e40e5b3018bfec136452cd3ff6ac59

        self.subscriber.set_message_handler(self.handle_device_message)

        for topic in MQTT_SUBSCRIPTION_TOPICS:
            self.subscriber.subscribe(topic, qos=1)

    def start(self):

        if self._started:
            logger.warning("MQTT service is already running.")
            return

        # Connect to MQTT broker
        self.client.connect()

        # Subscribe to configured topics
        subscribed_topics = set(MQTT_SUBSCRIPTION_TOPICS)

        subscribed_topics.add(DEVICE_STATUS)

        for topic in subscribed_topics:
            self.subscriber.subscribe(
                topic,
                qos=1,
            )

        self._started = True

        logger.info("MQTT service started successfully.")

    def stop(self):

        if not self._started:
            return

        self.client.disconnect()
        self._started = False

        logger.info("MQTT service stopped successfully.")

    
    def handle_ack_message(self, topic, payload, controller_id):
        """
        Store controller ACK and update the matching StageBatch.
        """

        # Decode JSON payload
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except (json.JSONDecodeError, TypeError):
            logger.exception("Invalid ACK JSON received from %s", controller_id)
            return

        if not isinstance(data, dict):
            logger.warning("ACK payload must be a JSON object: %s", controller_id)
            return

        payload_controller = str(
            data.get("controller_id", "")
        ).strip()

        event = str(data.get("event", "")).strip().upper()

        if not payload_controller or payload_controller.lower() != controller_id.lower():
            logger.warning("ACK controller ID mismatch: %s", controller_id)
            return

        # Find the treatment stage
        stage = TreatmentStage.objects.filter(
            controller_id__iexact=controller_id
        ).first()

        if not stage:
            logger.warning("No treatment stage found for controller %s", controller_id)
            return

        device_id = data.get("device_id")
        device_date = data.get("date")
        device_time = data.get("time")
        reason = data.get("reason")

        with transaction.atomic():

            # Find the latest active batch for this stage
            batch = (
                StageBatch.objects.select_for_update()
                .filter(
                    stage=stage,
                    status__in=["SENT"],
                )
                .order_by("-created_at")
                .first()
            )

            # Save every valid ACK, even if no batch matches
            event_log = StageBatchEventLog.objects.create(
                stage_batch=batch,
                stage=stage,
                controller_id=controller_id,
                device_id=device_id,
                topic=topic,
                message_type="ACK",
                event=event,
                reason=reason,
                device_date=device_date,
                device_time=device_time,
                raw_payload=(
                    payload if isinstance(payload, str)
                    else json.dumps(payload)
                ),
                parsed_payload=data,
            )

            if not batch:
                logger.warning(
                    "ACK stored without matching active batch. Controller: %s",
                    controller_id,
                )
                return

            # Update batch only for the expected ACK event
            if event == "COMMAND_RECEIVED" and batch.status == "SENT":
                batch.status = "PENDING"
                batch.save(update_fields=["status", "updated_at"])

                logger.info(
                    "STAGE BATCH UPDATED | Batch: %s | SENT -> PENDING",
                    batch.batch_number,
                )

            logger.info(
                "ACK STORED | Event Log ID: %s | Batch: %s",
                event_log.id,
                batch.batch_number,
            )

    
    
    def handle_status_message(self, topic, payload, controller_id):
        """
        Process controller STATUS messages.
        Store every event, track equipment execution, and update
        only the configuration belonging to the equipment that changed.
        """

        # 1. Decode payload
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except (json.JSONDecodeError, TypeError):
            logger.exception("Invalid STATUS JSON from %s", controller_id)
            return

        if not isinstance(data, dict):
            logger.warning("STATUS payload must be a JSON object")
            return

        # 2. Validate controller
        payload_controller = str(
            data.get("controller_id", "")
        ).strip()

        if (
            not payload_controller
            or payload_controller.lower() != controller_id.lower()
        ):
            logger.warning("STATUS controller ID mismatch: %s", controller_id)
            return

        event = str(data.get("event", "")).strip().upper()
        device_id = str(data.get("device_id", "")).strip()

        if not event:
            logger.warning("STATUS event is missing from %s", controller_id)
            return

        # 3. Find treatment stage
        stage = TreatmentStage.objects.filter(
            controller_id__iexact=controller_id
        ).first()

        if not stage:
            logger.warning("No treatment stage found for %s", controller_id)
            return

        # 4. Identify equipment using device_id
        equipment = None

        if device_id:
            equipment = stage.equipments.filter(
                code__iexact=device_id
            ).first()

        if (
            device_id
            and not equipment
            and device_id.lower() != controller_id.lower()
        ):
            logger.warning(
                "Equipment %s not found under stage %s",
                device_id,
                stage.name,
            )

        # 5. Define event-specific equipment transitions
        event_mapping = {
            "VALVE_OPENED": {
                "operation": "VALVE",
                "payload_field": "valve",
                "expected_state": "ON",
                "new_state": "ON",
                "action": "START",
            },
            "VALVE_CLOSED": {
                "operation": "VALVE",
                "payload_field": "valve",
                "expected_state": "OFF",
                "new_state": "OFF",
                "action": "END",
            },
            "PUMP_STARTED": {
                "operation": "PUMP",
                "payload_field": "pump",
                "expected_state": "ON",
                "new_state": "ON",
                "action": "START",
            },
            "PUMP_STOPPED": {
                "operation": "PUMP",
                "payload_field": "pump",
                "expected_state": "OFF",
                "new_state": "OFF",
                "action": "END",
            },
        }

        raw_payload = (
            payload if isinstance(payload, str)
            else json.dumps(payload)
        )

        with transaction.atomic():

            # 6. Find latest active batch
            batch = (
                StageBatch.objects.select_for_update()
                .filter(
                    stage=stage,
                    status__in=["SENT", "PENDING", "RUNNING"],
                )
                .order_by("-created_at")
                .first()
            )

            # 7. Store every STATUS event
            event_log = StageBatchEventLog.objects.create(
                stage_batch=batch,
                stage=stage,
                equipment=equipment,
                controller_id=controller_id,
                device_id=device_id,
                topic=topic,
                message_type="STATUS",
                event=event,
                state=data.get("state"),
                reason=data.get("reason"),
                device_date=data.get("date"),
                device_time=data.get("time"),
                raw_payload=raw_payload,
                parsed_payload=data,
            )

            if not batch:
                logger.warning(
                    "STATUS stored without active batch | Controller: %s | Event: %s",
                    controller_id,
                    event,
                )
                return

            # 8. Validate the event against its corresponding payload field
            transition = event_mapping.get(event)
            valid_transition = False

            if transition and equipment:
                reported_state = str(
                    data.get(transition["payload_field"], "")
                ).strip().upper()

                if reported_state == transition["expected_state"]:
                    valid_transition = True
                else:
                    logger.warning(
                        "Event/state mismatch | Event: %s | Device: %s | "
                        "Expected: %s | Received: %s",
                        event,
                        device_id,
                        transition["expected_state"],
                        reported_state,
                    )

            # 9. Update only the matching equipment configuration
            if valid_transition:

                config = StageEquipmentConfig.objects.filter(
                    stage=stage,
                    equipment=equipment,
                    is_active=True,
                ).first()

                if not config:
                    logger.warning(
                        "Active equipment configuration not found | "
                        "Stage: %s | Equipment: %s",
                        stage.name,
                        equipment.code,
                    )
                else:
                    received_time = timezone.localtime(
                        event_log.received_at
                    ).time()

                    if transition["action"] == "START":

                        # Do not reset the start time for duplicate start events.
                        if config.current_state != "ON":
                            config.current_state = "ON"
                            config.start_time = received_time
                            config.end_time = None
                            config.duration_seconds = None

                            config.save(
                                update_fields=[
                                    "current_state",
                                    "start_time",
                                    "end_time",
                                    "duration_seconds",
                                    "updated_at",
                                ]
                            )

                    elif transition["action"] == "END":

                        config.current_state = "OFF"
                        config.end_time = received_time

                        config.save(
                            update_fields=[
                                "current_state",
                                "end_time",
                                "updated_at",
                            ]
                        )

            # 10. Track equipment execution
            if valid_transition:

                operation = transition["operation"]

                if transition["action"] == "START":

                    existing_execution = (
                        StageBatchEquipmentExecution.objects.filter(
                            stage_batch=batch,
                            equipment=equipment,
                            operation_name=operation,
                            status="RUNNING",
                        ).first()
                    )

                    if not existing_execution:
                        StageBatchEquipmentExecution.objects.create(
                            stage_batch=batch,
                            equipment=equipment,
                            operation_name=operation,
                            start_event=event,
                            started_at=event_log.received_at,
                            status="RUNNING",
                        )

                        logger.info(
                            "%s EXECUTION STARTED | Batch: %s | Equipment: %s",
                            operation,
                            batch.batch_number,
                            equipment.code,
                        )

                elif transition["action"] == "END":

                    execution = (
                        StageBatchEquipmentExecution.objects.filter(
                            stage_batch=batch,
                            equipment=equipment,
                            operation_name=operation,
                            status="RUNNING",
                        )
                        .order_by("-started_at")
                        .first()
                    )

                    if execution:
                        completed_at = event_log.received_at

                        execution.end_event = event
                        execution.completed_at = completed_at
                        execution.duration_seconds = max(
                            0,
                            int(
                                (
                                    completed_at - execution.started_at
                                ).total_seconds()
                            ),
                        )
                        execution.status = "COMPLETED"

                        execution.save(
                            update_fields=[
                                "end_event",
                                "completed_at",
                                "duration_seconds",
                                "status",
                                "updated_at",
                            ]
                        )

                        # Store the completed execution duration in config.
                        StageEquipmentConfig.objects.filter(
                            stage=stage,
                            equipment=equipment,
                            is_active=True,
                        ).update(
                            duration_seconds=execution.duration_seconds
                        )

                        logger.info(
                            "%s EXECUTION COMPLETED | Batch: %s | "
                            "Equipment: %s | Duration: %s seconds",
                            operation,
                            batch.batch_number,
                            equipment.code,
                            execution.duration_seconds,
                        )

                    else:
                        logger.warning(
                            "No running %s execution found | Batch: %s | Equipment: %s",
                            operation,
                            batch.batch_number,
                            equipment.code,
                        )

            # 11. Update overall batch completion
            if event == "CYCLE_COMPLETED":

                if batch.status in ["SENT", "PENDING", "RUNNING"]:
                    batch.status = "COMPLETED"
                    batch.completed_at = event_log.received_at

                    if not batch.started_at:
                        batch.started_at = batch.created_at

                    batch.save(
                        update_fields=[
                            "status",
                            "started_at",
                            "completed_at",
                            "updated_at",
                        ]
                    )

                    logger.info(
                        "STAGE BATCH COMPLETED | Batch: %s",
                        batch.batch_number,
                    )

            elif (
                valid_transition
                and transition["action"] == "START"
                and batch.status == "PENDING"
            ):
                batch.status = "RUNNING"

                if not batch.started_at:
                    batch.started_at = event_log.received_at

                batch.save(
                    update_fields=[
                        "status",
                        "started_at",
                        "updated_at",
                    ]
                )

            logger.info(
                "STATUS EVENT STORED | Log ID: %s | Event: %s | Batch: %s",
                event_log.id,
                event,
                batch.batch_number,
            )


    def handle_device_message(self, message):
        """
        Central handler for incoming controller/device messages.
        Supports dynamic controller IDs.
        """

        topic = message.topic
        payload = self.subscriber.decode_message(message)

        topic_parts = topic.split("/")

        if len(topic_parts) != 4 or topic_parts[0:2] != ["aquapod", "test"]:
            logger.warning("Unknown MQTT topic received: %s", topic)
            return

        controller_id = topic_parts[2]
        message_type = topic_parts[3].lower()

        logger.info(
            "MQTT MESSAGE RECEIVED | Controller: %s | Type: %s | Payload: %s",
            controller_id,
            message_type,
            payload,
        )

        if message_type == "ack":
            self.handle_ack_message(
                topic=topic,
                payload=payload,
                controller_id=controller_id,
            )
            logger.info("CONTROLLER ACK RECEIVED | %s", controller_id)


<<<<<<< HEAD
    def handle_device_status(self, device_code, payload):

        try:

            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")

            if isinstance(payload, str):
                payload = json.loads(payload)

            if not isinstance(payload, dict):
                logger.warning(
                    "Invalid device status payload: %s",
                    payload,
                )
                return

            state = payload.get("state")

            logger.info(
                "DEVICE: %s | STATE: %s",
                device_code,
                state,
            )

        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.exception(
                "Unable to decode device status for %s",
                device_code,
=======
        elif message_type == "status":
            self.handle_status_message(
                topic=topic,
                payload=payload,
                controller_id=controller_id,
>>>>>>> fbbd939aa1e40e5b3018bfec136452cd3ff6ac59
            )
            logger.info("CONTROLLER STATUS RECEIVED | %s", controller_id)

        elif message_type == "alert":
            logger.info("CONTROLLER ALERT RECEIVED | %s", controller_id)

        elif message_type == "power":
            logger.info("CONTROLLER POWER RECEIVED | %s", controller_id)

        elif message_type == "heartbeat":
            logger.info("CONTROLLER HEARTBEAT RECEIVED | %s", controller_id)

        else:
            logger.warning("Unsupported MQTT message type: %s", message_type)


    @property
    def is_running(self):
        return self._started

    @property
    def is_connected(self):
        return self.client.is_connected