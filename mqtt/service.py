import logging
import json

from .client import MQTTClient
from .publisher import MQTTPublisher
from .subscriber import MQTTSubscriber
from .topics import MQTT_SUBSCRIPTION_TOPICS
from django.utils import timezone
from django.db import transaction

from .topics import (
    MQTT_VALVE_ACK_TOPIC,
    MQTT_VALVE_STATUS_TOPIC,
    MQTT_SUBSCRIPTION_TOPICS,
    DEVICE_STATUS,
)
from treatment_process.models import (
    TreatmentStage,
    StageBatch,
    StageBatchEventLog,
    StageBatchEquipmentExecution,
    StageEquipmentConfig,
)

# Import Alert models (adjust the path according to your project structure)
from alerts.models import AlertType, Alert

logger = logging.getLogger(__name__)


class MQTTService:
    """
    Main service that connects to MQTT broker, subscribes to topics,
    and processes incoming messages from controllers (ACK, STATUS, POWER, etc.)
    """

    def __init__(self):
        self.client = MQTTClient()
        self._started = False

        self.publisher = MQTTPublisher(self.client)
        self.subscriber = MQTTSubscriber(self.client)

        # Set the main message handler
        self.subscriber.set_message_handler(self.handle_device_message)

        # Subscribe to all configured topics at startup
        for topic in MQTT_SUBSCRIPTION_TOPICS:
            self.subscriber.subscribe(topic, qos=1)

    def start(self):
        """Start the MQTT service (connect + subscribe)."""
        if self._started:
            logger.warning("MQTT service is already running.")
            return

        # Connect to MQTT broker
        self.client.connect()

        # Make sure we subscribe to all required topics
        subscribed_topics = set(MQTT_SUBSCRIPTION_TOPICS)
        subscribed_topics.add(DEVICE_STATUS)

        for topic in subscribed_topics:
            self.subscriber.subscribe(topic, qos=1)

        self._started = True
        logger.info("MQTT service started successfully.")

    def stop(self):
        """Stop the MQTT service and disconnect from broker."""
        if not self._started:
            return

        self.client.disconnect()
        self._started = False
        logger.info("MQTT service stopped successfully.")

    # ------------------------------------------------------------------
    # ACK Handler
    # ------------------------------------------------------------------
    def handle_ack_message(self, topic, payload, controller_id):
        """
        Process ACK messages from controller.
        - Stores the ACK in StageBatchEventLog
        - Moves StageBatch from SENT → PENDING when COMMAND_RECEIVED is received
        """
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except (json.JSONDecodeError, TypeError):
            logger.exception("Invalid ACK JSON received from %s", controller_id)
            return

        if not isinstance(data, dict):
            logger.warning("ACK payload must be a JSON object: %s", controller_id)
            return

        payload_controller = str(data.get("controller_id", "")).strip()
        event = str(data.get("event", "")).strip().upper()

        # Validate controller_id
        if (
            not payload_controller
            or payload_controller.lower() != controller_id.lower()
        ):
            logger.warning("ACK controller ID mismatch: %s", controller_id)
            return

        # Find the related TreatmentStage
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
            # Look for the latest batch that is still in SENT status
            batch = (
                StageBatch.objects.select_for_update()
                .filter(stage=stage, status__in=["SENT"])
                .order_by("-created_at")
                .first()
            )

            # Always store the ACK event (even if no batch found)
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
                    payload if isinstance(payload, str) else json.dumps(payload)
                ),
                parsed_payload=data,
            )

            if not batch:
                logger.warning(
                    "ACK stored without matching active batch. Controller: %s",
                    controller_id,
                )
                return

            # Move batch from SENT → PENDING when we receive COMMAND_RECEIVED
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

    # ------------------------------------------------------------------
    # STATUS Handler
    # ------------------------------------------------------------------
    def handle_status_message(self, topic, payload, controller_id):
        """
        Process STATUS messages from controller.
        - Stores every event in StageBatchEventLog
        - Updates StageEquipmentConfig (ON/OFF + timestamps)
        - Creates / completes StageBatchEquipmentExecution records
        - Moves batch to RUNNING or COMPLETED when appropriate
        """
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except (json.JSONDecodeError, TypeError):
            logger.exception("Invalid STATUS JSON from %s", controller_id)
            return

        if not isinstance(data, dict):
            logger.warning("STATUS payload must be a JSON object")
            return

        # Validate controller
        payload_controller = str(data.get("controller_id", "")).strip()
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

        # Find treatment stage
        stage = TreatmentStage.objects.filter(
            controller_id__iexact=controller_id
        ).first()

        if not stage:
            logger.warning("No treatment stage found for %s", controller_id)
            return

        # Try to find the equipment by device_id
        equipment = None
        if device_id:
            equipment = stage.equipments.filter(code__iexact=device_id).first()

        if device_id and not equipment and device_id.lower() != controller_id.lower():
            logger.warning(
                "Equipment %s not found under stage %s",
                device_id,
                stage.name,
            )

        # Mapping of important events → how we should treat them
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

        raw_payload = payload if isinstance(payload, str) else json.dumps(payload)

        with transaction.atomic():
            # Find latest open batch
            batch = (
                StageBatch.objects.select_for_update()
                .filter(stage=stage, status__in=["SENT", "PENDING", "RUNNING"])
                .order_by("-created_at")
                .first()
            )

            # Always store the event
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

            # Validate the event against the payload field
            transition = event_mapping.get(event)
            valid_transition = False

            if transition and equipment:
                reported_state = (
                    str(data.get(transition["payload_field"], "")).strip().upper()
                )

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

            # Update StageEquipmentConfig (start/end time + state)
            if valid_transition:
                config = StageEquipmentConfig.objects.filter(
                    stage=stage,
                    equipment=equipment,
                    is_active=True,
                ).first()

                if not config:
                    logger.warning(
                        "Active equipment configuration not found | Stage: %s | Equipment: %s",
                        stage.name,
                        equipment.code,
                    )
                else:
                    received_time = timezone.localtime(event_log.received_at).time()

                    if transition["action"] == "START":
                        # Only set start_time if it was previously OFF
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
                            update_fields=["current_state", "end_time", "updated_at"]
                        )

            if valid_transition:
                operation = transition["operation"]

                if transition["action"] == "START":
                    existing_execution = StageBatchEquipmentExecution.objects.filter(
                        stage_batch=batch,
                        equipment=equipment,
                        operation_name=operation,
                        status="RUNNING",
                    ).first()

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
                            int((completed_at - execution.started_at).total_seconds()),
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

                        StageEquipmentConfig.objects.filter(
                            stage=stage,
                            equipment=equipment,
                            is_active=True,
                        ).update(duration_seconds=execution.duration_seconds)

                        logger.info(
                            "%s EXECUTION COMPLETED | Batch: %s | Equipment: %s | Duration: %s s",
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

            # Update overall batch status
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
                    logger.info("STAGE BATCH COMPLETED | Batch: %s", batch.batch_number)

            elif (
                valid_transition
                and transition["action"] == "START"
                and batch.status == "PENDING"
            ):
                batch.status = "RUNNING"
                if not batch.started_at:
                    batch.started_at = event_log.received_at
                batch.save(update_fields=["status", "started_at", "updated_at"])

            logger.info(
                "STATUS EVENT STORED | Log ID: %s | Event: %s | Batch: %s",
                event_log.id,
                event,
                batch.batch_number,
            )

    # -----------------------------------------------------------------
    # POWER Handler  ←  METHOD
    # ------------------------------------------------------------------

    def handle_power_message(self, topic, payload, controller_id):

        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
        except (json.JSONDecodeError, TypeError):
            logger.exception("Invalid POWER JSON from %s", controller_id)
            return

        if not isinstance(data, dict):
            logger.warning("POWER payload must be a JSON object")
            return

        event = str(data.get("event", "")).strip().upper()
        reason = str(data.get("reason", "")).strip().upper()
        status_value = str(data.get("status", "")).strip().upper()
        device_id = str(data.get("device_id") or controller_id).strip()

        stage = TreatmentStage.objects.filter(
            controller_id__iexact=controller_id
        ).first()

        # ======================================================
        # MQTT CONNECTION RESTORED - ONLINE
        # ======================================================
                
        if status_value == "ONLINE":

            alert_type = AlertType.objects.filter(
                code="MQTT_CONNECTION_RESTORED",
                is_active=True,
            ).first()

            if not alert_type:
                logger.error("MQTT_CONNECTION_RESTORED AlertType not found")
                return

            title = "Controller ONLINE"
            message = f"Controller {device_id} is ONLINE. MQTT connection restored."

            Alert.objects.create(
                stage=stage,
                alert_type=alert_type,
                title=title,
                message=message,
                source="SYSTEM",
                severity="MEDIUM",
                status="ACTIVE",
                triggered_at=timezone.now(),
                remarks=(
                    f"Controller: {controller_id} | "
                    f"Device: {device_id} | "
                    f"Status: {status_value} | "
                    f"Topic: {topic} | "
                    f"Payload: {json.dumps(data)}"
                ),
            )

            logger.info(
                "CONTROLLER ONLINE ALERT CREATED | Device: %s",
                device_id,
            )

            return

        
        # ======================================================
        # MQTT CONNECTION LOST - OFFLINE
        # ======================================================

        if status_value == "OFFLINE" or reason == "MQTT_CONNECTION_LOST":

            alert_type = AlertType.objects.filter(
                code="MQTT_CONNECTION_LOST",
                category="SYSTEM",
                is_active=True,
            ).first()

            if not alert_type:
                logger.error("MQTT_CONNECTION_LOST AlertType not found")
                return

            title = "Controller OFFLINE"
            message = f"Controller {device_id} is OFFLINE due to MQTT connection loss."

            alert = Alert.objects.create(
                stage=stage,
                alert_type=alert_type,
                title=title,
                message=message,
                source="SYSTEM",
                severity="HIGH",
                status="ACTIVE",
                triggered_at=timezone.now(),
                remarks=(
                    f"Controller: {controller_id} | "
                    f"Device: {device_id} | "
                    f"Status: {status_value} | "
                    f"Reason: {reason} | "
                    f"Topic: {topic} | "
                    f"Payload: {json.dumps(data)}"
                ),
            )

            logger.info(
                "CONTROLLER OFFLINE ALERT CREATED | Alert ID: %s | Device: %s",
                alert.id,
                device_id,
            )

            return

        # ======================================================
        # ACTUAL POWER ON / OFF
        # ======================================================

        if event in ("POWER_ON", "ON", "POWERON", "POWER_RESTORED"):

            alert_code = "POWER_ON"
            title = "Stage Power ON"
            severity = "MEDIUM"
            message = f"Power restored on device {device_id}"

        elif event in ("POWER_OFF", "OFF", "POWEROFF", "POWER_LOST"):

            alert_code = "POWER_OFF"
            title = "Stage Power OFF"
            severity = "HIGH"
            message = f"Power lost on device {device_id}"

        else:
            logger.warning(
                "Unknown POWER event '%s' from %s",
                event,
                controller_id,
            )
            return

        alert_type = AlertType.objects.filter(
            code=alert_code,
            category="STAGE",
            is_active=True,
        ).first()

        if not alert_type:
            logger.error(
                "AlertType with code=%s and category=STAGE not found",
                alert_code,
            )
            return

        Alert.objects.create(
            stage=stage,
            alert_type=alert_type,
            title=title,
            message=message,
            source="SYSTEM",
            severity=severity,
            status="ACTIVE",
            triggered_at=timezone.now(),
            remarks=(
                f"Controller: {controller_id} | "
                f"Stage: {stage.name if stage else 'Not mapped'} | "
                f"Device: {device_id} | "
                f"Status: {status_value} | "
                f"Reason: {reason} | "
                f"Topic: {topic} | "
                f"Payload: {json.dumps(data)}"
            ),
        )

        logger.info(
            "%s ALERT CREATED | Device: %s | Stage: %s",
            alert_code,
            device_id,
            stage.name if stage else "Not mapped",
        )


    # ------------------------------------------------------------------
    # Main message router
    # ------------------------------------------------------------------
    def handle_device_message(self, message):

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

        elif message_type == "status":
            self.handle_status_message(
                topic=topic,
                payload=payload,
                controller_id=controller_id,
            )
            logger.info("CONTROLLER STATUS RECEIVED | %s", controller_id)

        elif message_type == "alert":
            logger.info("CONTROLLER ALERT RECEIVED | %s", controller_id)

        elif message_type == "power":
            self.handle_power_message(
                topic=topic,
                payload=payload,
                controller_id=controller_id,
            )
            logger.info("CONTROLLER POWER RECEIVED | %s", controller_id)

        elif message_type == "heartbeat":
            logger.info("CONTROLLER HEARTBEAT RECEIVED | %s", controller_id)

        else:
            logger.warning("Unsupported MQTT message type: %s", message_type)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def is_running(self):
        return self._started

    @property
    def is_connected(self):
        return self.client.is_connected
