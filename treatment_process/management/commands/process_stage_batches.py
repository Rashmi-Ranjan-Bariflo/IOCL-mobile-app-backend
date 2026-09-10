# from django.core.management.base import BaseCommand
# from django.db import transaction
# from django.utils import timezone

# from treatment_process.models import (
#     StageBatch,
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )

# from treatment_process.services import (
#     StageExecutionService,
# )


# class Command(BaseCommand):

#     help = (
#         "Process waiting treatment stage "
#         "equipment executions."
#     )

#     def handle(self, *args, **options):

#         self.stdout.write(
#             "Treatment process worker started."
#         )

#         while True:

#             try:

#                 self.process_waiting_equipment()

#                 self.process_pending_stages()

#             except Exception as exc:

#                 self.stderr.write(
#                     f"Worker error: {exc}"
#                 )

#             # -------------------------------------------------
#             # IMPORTANT:
#             #
#             # This worker polling delay is NOT part of the
#             # equipment duration.
#             #
#             # It is only how frequently we check the database.
#             # -------------------------------------------------

#             import time

#             time.sleep(1)

#     # =========================================================
#     # PROCESS WAITING EQUIPMENT
#     # =========================================================

#     def process_waiting_equipment(self):

#         now = timezone.now()

#         waiting_executions = (
#             StageBatchProcessEquipmentExecution.objects
#             .filter(
#                 status="WAITING",
#                 scheduled_at__lte=now,
#             )
#             .select_related(
#                 "equipment",
#                 "stage_batch_process_execution",
#                 "stage_batch_process_execution__stage_batch",
#             )
#             .order_by(
#                 "scheduled_at"
#             )
#         )

#         for equipment_execution in waiting_executions:

#             self.resume_equipment_execution(
#                 equipment_execution
#             )

#     # =========================================================
#     # RESUME EQUIPMENT EXECUTION
#     # =========================================================

#     def resume_equipment_execution(
#         self,
#         equipment_execution,
#     ):

#         with transaction.atomic():

#             equipment_execution = (
#                 StageBatchProcessEquipmentExecution
#                 .objects
#                 .select_for_update()
#                 .select_related(
#                     "equipment",
#                     "stage_batch_process_execution",
#                     "stage_batch_process_execution__stage_batch",
#                 )
#                 .filter(
#                     id=equipment_execution.id,
#                     status="WAITING",
#                 )
#                 .first()
#             )

#             if not equipment_execution:

#                 return

#             equipment = (
#                 equipment_execution.equipment
#             )

#             process_execution = (
#                 equipment_execution
#                 .stage_batch_process_execution
#             )

#             stage_batch = (
#                 process_execution.stage_batch
#             )

#             # -------------------------------------------------
#             # Check again.
#             # -------------------------------------------------

#             if equipment.duration_seconds is not None:

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 if not service.is_duration_completed(
#                     equipment
#                 ):

#                     return

#             # -------------------------------------------------
#             # Turn equipment OFF.
#             # -------------------------------------------------

#             service = StageExecutionService(
#                 stage_batch
#             )

#             service.turn_equipment_off(
#                 equipment
#             )

#             # -------------------------------------------------
#             # Complete equipment execution.
#             # -------------------------------------------------

#             equipment_execution.complete_execution(
#                 state="OFF"
#             )

#             # -------------------------------------------------
#             # Complete the process.
#             # -------------------------------------------------

#             process_execution.complete_process()

#         # -----------------------------------------------------
#         # Continue the stage OUTSIDE the transaction.
#         # -----------------------------------------------------

#         try:

#             service = StageExecutionService(
#                 stage_batch
#             )

#             service.execute()

#         except Exception as exc:

#             stage_batch.fail_batch()

#             service.deactivate_stage_equipment()

#             self.stderr.write(
#                 f"Stage {stage_batch.id} failed: {exc}"
#             )

#     # =========================================================
#     # START PENDING STAGES
#     # =========================================================

#     def process_pending_stages(self):

#         running_stages = (
#             StageBatch.objects
#             .filter(
#                 status="RUNNING"
#             )
#             .order_by(
#                 "created_at"
#             )
#         )

#         for stage_batch in running_stages:

#             # -------------------------------------------------
#             # If the stage already has a WAITING equipment
#             # execution, do not execute another process.
#             # -------------------------------------------------

#             has_waiting_equipment = (
#                 StageBatchProcessEquipmentExecution
#                 .objects
#                 .filter(
#                     stage_batch_process_execution__stage_batch=stage_batch,
#                     status="WAITING",
#                 )
#                 .exists()
#             )

#             if has_waiting_equipment:

#                 continue

#             # -------------------------------------------------
#             # Find current process.
#             # -------------------------------------------------

#             has_running_process = (
#                 StageBatchProcessExecution
#                 .objects
#                 .filter(
#                     stage_batch=stage_batch,
#                     status="RUNNING",
#                 )
#                 .exists()
#             )

#             if has_running_process:

#                 continue

#             # -------------------------------------------------
#             # Execute next process.
#             # -------------------------------------------------

#             try:

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 service.execute()

#             except Exception as exc:

#                 stage_batch.fail_batch()

#                 service.deactivate_stage_equipment()

#                 self.stderr.write(
#                     f"Stage {stage_batch.id} failed: {exc}"
#                 )






# import time

# from django.core.management.base import BaseCommand
# from django.db import transaction
# from django.utils import timezone

# from treatment_process.models import (
#     StageBatch,
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )

# from treatment_process.services.stage_controller import (
#     StageExecutionService,
# )


# class Command(BaseCommand):

#     help = (
#         "Process waiting treatment stage "
#         "equipment executions."
#     )

#     def handle(self, *args, **options):

#         self.stdout.write(
#             "Treatment process worker started."
#         )

#         while True:

#             try:

#                 # -------------------------------------------------
#                 # First process timed equipment whose scheduled
#                 # time has arrived.
#                 # -------------------------------------------------

#                 self.process_waiting_equipment()

#                 # -------------------------------------------------
#                 # Then process stages that can continue.
#                 # -------------------------------------------------

#                 self.process_pending_stages()

#             except Exception as exc:

#                 self.stderr.write(
#                     f"Worker error: {exc}"
#                 )

#             # -------------------------------------------------
#             # IMPORTANT:
#             #
#             # This sleep is ONLY worker polling delay.
#             #
#             # It is NOT equipment duration.
#             # -------------------------------------------------

#             time.sleep(1)

#     # =========================================================
#     # PROCESS WAITING EQUIPMENT
#     # =========================================================

#     def process_waiting_equipment(self):

#         now = timezone.now()

#         waiting_executions = (
#             StageBatchProcessEquipmentExecution.objects
#             .filter(
#                 status="WAITING",
#                 scheduled_at__lte=now,
#                 stage_batch_process_execution__stage_batch__status="RUNNING",
#             )
#             .select_related(
#                 "equipment",
#                 "stage_batch_process_execution",
#                 "stage_batch_process_execution__stage_batch",
#             )
#             .order_by(
#                 "scheduled_at"
#             )
#         )

#         for equipment_execution in waiting_executions:

#             self.resume_equipment_execution(
#                 equipment_execution
#             )

#     # =========================================================
#     # RESUME EQUIPMENT EXECUTION
#     # =========================================================

#     def resume_equipment_execution(
#         self,
#         equipment_execution,
#     ):

#         stage_batch = None

#         try:

#             with transaction.atomic():

#                 # -------------------------------------------------
#                 # Lock the equipment execution so that two worker
#                 # iterations cannot process the same record.
#                 # -------------------------------------------------

#                 equipment_execution = (
#                     StageBatchProcessEquipmentExecution
#                     .objects
#                     .select_for_update()
#                     .select_related(
#                         "equipment",
#                         "stage_batch_process_execution",
#                         "stage_batch_process_execution__stage_batch",
#                     )
#                     .filter(
#                         id=equipment_execution.id,
#                         status="WAITING",
#                     )
#                     .first()
#                 )

#                 if not equipment_execution:

#                     return

#                 equipment = (
#                     equipment_execution.equipment
#                 )

#                 process_execution = (
#                     equipment_execution
#                     .stage_batch_process_execution
#                 )

#                 stage_batch = (
#                     process_execution.stage_batch
#                 )

#                 # -------------------------------------------------
#                 # IMPORTANT:
#                 #
#                 # If STOP was pressed before this worker picked
#                 # up the execution, do NOT continue it.
#                 # -------------------------------------------------

#                 if stage_batch.status != "RUNNING":

#                     return

#                 # -------------------------------------------------
#                 # Check whether the scheduled time has really
#                 # arrived.
#                 # -------------------------------------------------

#                 if (
#                     equipment_execution.scheduled_at
#                     and timezone.now()
#                     < equipment_execution.scheduled_at
#                 ):

#                     return

#                 # -------------------------------------------------
#                 # Turn equipment OFF.
#                 # -------------------------------------------------

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 service.turn_equipment_off(
#                     equipment
#                 )

#                 # -------------------------------------------------
#                 # Complete equipment execution.
#                 # -------------------------------------------------

#                 equipment_execution.complete_execution(
#                     state="OFF"
#                 )

#             # -----------------------------------------------------
#             # Continue process OUTSIDE the transaction.
#             # -----------------------------------------------------

#             if stage_batch.status != "RUNNING":

#                 return

#             service = StageExecutionService(
#                 stage_batch
#             )

#             service.execute()

#         except Exception as exc:

#             if stage_batch:

#                 try:

#                     stage_batch.refresh_from_db(
#                         fields=["status"]
#                     )

#                     if stage_batch.status == "RUNNING":

#                         stage_batch.fail_batch()

#                         service = StageExecutionService(
#                             stage_batch
#                         )

#                         service.deactivate_stage_equipment()

#                 except Exception as cleanup_exc:

#                     self.stderr.write(
#                         f"Stage {stage_batch.id} "
#                         f"cleanup failed: {cleanup_exc}"
#                     )

#                 self.stderr.write(
#                     f"Stage {stage_batch.id} "
#                     f"failed: {exc}"
#                 )

#     # =========================================================
#     # PROCESS RUNNING STAGES
#     # =========================================================

#     def process_pending_stages(self):

#         running_stages = (
#             StageBatch.objects
#             .filter(
#                 status="RUNNING"
#             )
#             .order_by(
#                 "created_at"
#             )
#         )

#         for stage_batch in running_stages:

#             # -------------------------------------------------
#             # If this stage has a WAITING equipment execution,
#             # it is waiting for its scheduled time.
#             #
#             # Do not start another operation.
#             # -------------------------------------------------

#             has_waiting_equipment = (
#                 StageBatchProcessEquipmentExecution
#                 .objects
#                 .filter(
#                     stage_batch_process_execution__stage_batch=stage_batch,
#                     status="WAITING",
#                 )
#                 .exists()
#             )

#             if has_waiting_equipment:

#                 continue

#             # -------------------------------------------------
#             # Execute/continue the stage.
#             #
#             # StageExecutionService will:
#             #
#             # - continue a RUNNING process, OR
#             # - start the next PENDING process, OR
#             # - complete the stage.
#             # -------------------------------------------------

#             try:

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 service.execute()

#             except Exception as exc:

#                 try:

#                     stage_batch.refresh_from_db(
#                         fields=["status"]
#                     )

#                     if stage_batch.status == "RUNNING":

#                         stage_batch.fail_batch()

#                         service = StageExecutionService(
#                             stage_batch
#                         )

#                         service.deactivate_stage_equipment()

#                 except Exception as cleanup_exc:

#                     self.stderr.write(
#                         f"Stage {stage_batch.id} "
#                         f"cleanup failed: {cleanup_exc}"
#                     )

#                 self.stderr.write(
#                     f"Stage {stage_batch.id} "
#                     f"failed: {exc}"
#                 )





# import time

# from django.core.management.base import BaseCommand
# from django.db import transaction
# from django.utils import timezone

# from treatment_process.models import (
#     StageBatch,
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )

# from treatment_process.services.stage_controller import (
#     StageExecutionService,
# )


# class Command(BaseCommand):

#     help = (
#         "Process waiting treatment stage "
#         "equipment executions."
#     )

#     def handle(self, *args, **options):

#         self.stdout.write(
#             "Treatment process worker started."
#         )

#         while True:

#             try:

#                 # -------------------------------------------------
#                 # First process equipment executions that are
#                 # waiting for their scheduled OFF time.
#                 # -------------------------------------------------

#                 self.process_waiting_equipment()

#                 # -------------------------------------------------
#                 # Then process stages that can continue.
#                 # -------------------------------------------------

#                 self.process_pending_stages()

#             except Exception as exc:

#                 self.stderr.write(
#                     f"Worker error: {exc}"
#                 )

#             # -------------------------------------------------
#             # IMPORTANT:
#             #
#             # This sleep is ONLY worker polling delay.
#             #
#             # It is NOT equipment duration.
#             #
#             # The worker checks approximately every 1 second.
#             # -------------------------------------------------

#             time.sleep(1)

#     # =========================================================
#     # PROCESS WAITING EQUIPMENT
#     # =========================================================

#     def process_waiting_equipment(self):

#         now = timezone.now()

#         waiting_executions = (
#             StageBatchProcessEquipmentExecution.objects
#             .filter(
#                 status="WAITING",
#                 scheduled_at__lte=now,
#                 stage_batch_process_execution__stage_batch__status="RUNNING",
#             )
#             .select_related(
#                 "equipment",
#                 "stage_batch_process_execution",
#                 "stage_batch_process_execution__stage_batch",
#             )
#             .order_by(
#                 "scheduled_at"
#             )
#         )

#         for equipment_execution in waiting_executions:

#             self.resume_equipment_execution(
#                 equipment_execution
#             )

#     # =========================================================
#     # RESUME WAITING EQUIPMENT
#     # =========================================================

#     def resume_equipment_execution(
#         self,
#         equipment_execution,
#     ):

#         stage_batch = None

#         try:

#             with transaction.atomic():

#                 # -------------------------------------------------
#                 # Lock execution record.
#                 # -------------------------------------------------

#                 equipment_execution = (
#                     StageBatchProcessEquipmentExecution
#                     .objects
#                     .select_for_update()
#                     .select_related(
#                         "equipment",
#                         "stage_batch_process_execution",
#                         "stage_batch_process_execution__stage_batch",
#                     )
#                     .filter(
#                         id=equipment_execution.id,
#                         status="WAITING",
#                     )
#                     .first()
#                 )

#                 if not equipment_execution:

#                     return

#                 equipment = (
#                     equipment_execution.equipment
#                 )

#                 process_execution = (
#                     equipment_execution
#                     .stage_batch_process_execution
#                 )

#                 stage_batch = (
#                     process_execution.stage_batch
#                 )

#                 # -------------------------------------------------
#                 # STOP protection.
#                 # -------------------------------------------------

#                 if stage_batch.status != "RUNNING":

#                     return

#                 # -------------------------------------------------
#                 # Make sure scheduled time has arrived.
#                 # -------------------------------------------------

#                 if (
#                     equipment_execution.scheduled_at
#                     and timezone.now()
#                     < equipment_execution.scheduled_at
#                 ):

#                     return

#                 # -------------------------------------------------
#                 # Equipment should still be ON.
#                 #
#                 # If something else changed it meanwhile,
#                 # do not blindly turn it OFF.
#                 # -------------------------------------------------

#                 equipment.refresh_from_db()

#                 if equipment.current_state != "ON":

#                     equipment_execution.fail_execution(
#                         remarks=(
#                             f"Equipment '{equipment.name}' "
#                             "is no longer ON."
#                         )
#                     )

#                     return

#                 # -------------------------------------------------
#                 # Turn equipment OFF.
#                 # -------------------------------------------------

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 service.turn_equipment_off(
#                     equipment
#                 )

#                 # -------------------------------------------------
#                 # Complete the waiting equipment execution.
#                 # -------------------------------------------------

#                 equipment_execution.complete_execution(
#                     state="OFF"
#                 )

#             # -----------------------------------------------------
#             # Continue process OUTSIDE transaction.
#             # -----------------------------------------------------

#             stage_batch.refresh_from_db(
#                 fields=["status"]
#             )

#             if stage_batch.status != "RUNNING":

#                 return

#             service = StageExecutionService(
#                 stage_batch
#             )

#             service.execute()

#         except Exception as exc:

#             if stage_batch:

#                 try:

#                     stage_batch.refresh_from_db(
#                         fields=["status"]
#                     )

#                     if stage_batch.status == "RUNNING":

#                         stage_batch.fail_batch()

#                         service = StageExecutionService(
#                             stage_batch
#                         )

#                         service.deactivate_stage_equipment()

#                 except Exception as cleanup_exc:

#                     self.stderr.write(
#                         f"Stage {stage_batch.id} "
#                         f"cleanup failed: {cleanup_exc}"
#                     )

#                 self.stderr.write(
#                     f"Stage {stage_batch.id} "
#                     f"failed: {exc}"
#                 )

#     # =========================================================
#     # PROCESS RUNNING STAGES
#     # =========================================================

#     def process_pending_stages(self):

#         running_stages = (
#             StageBatch.objects
#             .filter(
#                 status="RUNNING"
#             )
#             .order_by(
#                 "created_at"
#             )
#         )

#         for stage_batch in running_stages:

#             # -------------------------------------------------
#             # If this stage has a WAITING equipment execution,
#             # it is waiting for its scheduled time.
#             #
#             # Do not start another operation.
#             # -------------------------------------------------

#             has_waiting_equipment = (
#                 StageBatchProcessEquipmentExecution
#                 .objects
#                 .filter(
#                     stage_batch_process_execution__stage_batch=stage_batch,
#                     status="WAITING",
#                 )
#                 .exists()
#             )

#             if has_waiting_equipment:

#                 continue

#             # -------------------------------------------------
#             # Continue or start the stage.
#             # -------------------------------------------------

#             try:

#                 service = StageExecutionService(
#                     stage_batch
#                 )

#                 service.execute()

#             except Exception as exc:

#                 try:

#                     stage_batch.refresh_from_db(
#                         fields=["status"]
#                     )

#                     if stage_batch.status == "RUNNING":

#                         stage_batch.fail_batch()

#                         service = StageExecutionService(
#                             stage_batch
#                         )

#                         service.deactivate_stage_equipment()

#                 except Exception as cleanup_exc:

#                     self.stderr.write(
#                         f"Stage {stage_batch.id} "
#                         f"cleanup failed: {cleanup_exc}"
#                     )

#                 self.stderr.write(
#                     f"Stage {stage_batch.id} "
#                     f"failed: {exc}"
#                 )






import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from treatment_process.models import (
    StageBatch,
    StageBatchProcessExecution,
    StageBatchProcessEquipmentExecution,
    StageEquipmentConfig,
)

from treatment_process.services.stage_controller import (
    StageExecutionService,
)


class Command(BaseCommand):

    help = (
        "Process waiting treatment stage "
        "equipment executions."
    )

    # =========================================================
    # WORKER
    # =========================================================

    def handle(
        self,
        *args,
        **options,
    ):
        """
        Continuously process treatment stage batches.

        The worker checks approximately every second.

        IMPORTANT:

        time.sleep(1) is ONLY the worker polling interval.

        It is NOT used for equipment duration.

        Equipment duration is calculated using:

            start_time
            duration_seconds
            scheduled_at
        """

        self.stdout.write(
            "Treatment stage execution worker started."
        )

        while True:

            try:

                # -------------------------------------------------
                # First process equipment that is waiting for
                # its configured OFF time.
                # -------------------------------------------------

                self.process_waiting_equipment()

                # -------------------------------------------------
                # Then continue stages that are ready to run.
                # -------------------------------------------------

                self.process_running_stages()

            except Exception as exc:

                self.stderr.write(
                    f"Worker error: {exc}"
                )

            # -----------------------------------------------------
            # Poll approximately once every second.
            #
            # This does NOT represent equipment duration.
            # -----------------------------------------------------

            time.sleep(1)

    # =========================================================
    # PROCESS WAITING EQUIPMENT
    # =========================================================

    def process_waiting_equipment(self):
        """
        Find equipment executions whose WAITING time has arrived.

        Example:

            Pump
                ON at 10:00:00
                duration = 30 sec

            scheduled_at
                10:00:30

        The worker checks every second.

            10:00:01 -> WAITING
            10:00:02 -> WAITING
            ...
            10:00:29 -> WAITING
            10:00:30 -> turn OFF
        """

        now = timezone.now()

        waiting_executions = (
            StageBatchProcessEquipmentExecution.objects
            .filter(
                status="WAITING",
                scheduled_at__lte=now,
                stage_batch_process_execution__stage_batch__status="RUNNING",
            )
            .select_related(
                "equipment",
                "stage_batch_process_execution",
                "stage_batch_process_execution__stage_batch",
            )
            .order_by(
                "scheduled_at",
            )
        )

        for equipment_execution in waiting_executions:

            self.resume_equipment_execution(
                equipment_execution
            )

    # =========================================================
    # RESUME WAITING EQUIPMENT
    # =========================================================

    def resume_equipment_execution(
        self,
        equipment_execution,
    ):
        """
        Resume an equipment execution after its configured
        duration has completed.

        Flow:

            WAITING
                ↓
            scheduled_at reached
                ↓
            get StageEquipmentConfig
                ↓
            confirm equipment is still ON
                ↓
            ON -> OFF
                ↓
            equipment execution COMPLETED
                ↓
            resume RUNNING process
        """

        stage_batch = None

        try:

            # -------------------------------------------------
            # Lock the execution record.
            #
            # This prevents two worker iterations from
            # processing the same WAITING record simultaneously.
            # -------------------------------------------------

            with transaction.atomic():

                equipment_execution = (
                    StageBatchProcessEquipmentExecution.objects
                    .select_for_update()
                    .select_related(
                        "equipment",
                        "stage_batch_process_execution",
                        "stage_batch_process_execution__stage_batch",
                    )
                    .filter(
                        id=equipment_execution.id,
                        status="WAITING",
                    )
                    .first()
                )

                if not equipment_execution:
                    return

                equipment = (
                    equipment_execution.equipment
                )

                process_execution = (
                    equipment_execution
                    .stage_batch_process_execution
                )

                stage_batch = (
                    process_execution.stage_batch
                )

                # -------------------------------------------------
                # STOP protection.
                # -------------------------------------------------

                if stage_batch.status != "RUNNING":
                    return

                # -------------------------------------------------
                # Make sure the scheduled time has actually
                # arrived.
                #
                # The query already checks this, but we check
                # again after acquiring the lock.
                # -------------------------------------------------

                if (
                    equipment_execution.scheduled_at
                    and timezone.now()
                    < equipment_execution.scheduled_at
                ):
                    return

                # -------------------------------------------------
                # Get the stage-specific runtime configuration.
                # -------------------------------------------------

                config = (
                    StageEquipmentConfig.objects
                    .filter(
                        stage=stage_batch.stage,
                        equipment=equipment,
                    )
                    .first()
                )

                if not config:

                    equipment_execution.fail_execution(
                        remarks=(
                            f"No StageEquipmentConfig found "
                            f"for equipment '{equipment.name}' "
                            f"in stage "
                            f"'{stage_batch.stage.name}'."
                        )
                    )

                    return

                # -------------------------------------------------
                # Safety check:
                #
                # The equipment should still be ON.
                #
                # If another operation already changed it,
                # do not blindly turn it OFF.
                # -------------------------------------------------

                if config.current_state != "ON":

                    equipment_execution.fail_execution(
                        remarks=(
                            f"Equipment '{equipment.name}' "
                            "is no longer ON."
                        )
                    )

                    return

                # -------------------------------------------------
                # Turn the stage configuration OFF.
                # -------------------------------------------------

                service = StageExecutionService(
                    stage_batch=stage_batch,
                )

                service.turn_equipment_off(
                    config=config,
                )

                # -------------------------------------------------
                # Complete the waiting equipment execution.
                # -------------------------------------------------

                equipment_execution.complete_execution(
                    state="OFF",
                )

            # -----------------------------------------------------
            # Continue the process OUTSIDE the transaction.
            #
            # This is important because we do not want the
            # process execution itself running inside the database
            # transaction.
            # -----------------------------------------------------

            stage_batch.refresh_from_db(
                fields=["status"]
            )

            if stage_batch.status != "RUNNING":
                return

            service = StageExecutionService(
                stage_batch=stage_batch,
            )

            service.execute()

        except Exception as exc:

            if stage_batch:

                try:

                    stage_batch.refresh_from_db(
                        fields=["status"]
                    )

                    if stage_batch.status == "RUNNING":

                        stage_batch.fail_batch()

                        service = StageExecutionService(
                            stage_batch=stage_batch,
                        )

                        service.deactivate_stage_equipment()

                except Exception as cleanup_exc:

                    self.stderr.write(
                        f"Stage {stage_batch.id} "
                        f"cleanup failed: {cleanup_exc}"
                    )

                self.stderr.write(
                    f"Stage {stage_batch.id} "
                    f"failed: {exc}"
                )

    # =========================================================
    # PROCESS RUNNING STAGES
    # =========================================================

    def process_running_stages(self):
        """
        Continue all currently RUNNING StageBatches.

        A stage with a WAITING equipment execution must not
        start another process.

        The waiting equipment is handled separately by:

            process_waiting_equipment()
        """

        running_stages = (
            StageBatch.objects
            .filter(
                status="RUNNING",
            )
            .order_by(
                "created_at",
            )
        )

        for stage_batch in running_stages:

            # -------------------------------------------------
            # If this stage has a WAITING equipment execution,
            # do not start another process.
            # -------------------------------------------------

            has_waiting_equipment = (
                StageBatchProcessEquipmentExecution.objects
                .filter(
                    stage_batch_process_execution__stage_batch=stage_batch,
                    status="WAITING",
                )
                .exists()
            )

            if has_waiting_equipment:
                continue

            # -------------------------------------------------
            # If there is already a RUNNING process, do not
            # start another one.
            #
            # The process will be continued by StageExecutionService.
            # -------------------------------------------------

            has_running_process = (
                StageBatchProcessExecution.objects
                .filter(
                    stage_batch=stage_batch,
                    status="RUNNING",
                )
                .exists()
            )

            # -------------------------------------------------
            # If a RUNNING process exists but has no WAITING
            # equipment, let the service continue it.
            #
            # Therefore we do NOT return here.
            # -------------------------------------------------

            try:

                service = StageExecutionService(
                    stage_batch=stage_batch,
                )

                service.execute()

            except Exception as exc:

                try:

                    stage_batch.refresh_from_db(
                        fields=["status"]
                    )

                    if stage_batch.status == "RUNNING":

                        stage_batch.fail_batch()

                        service = StageExecutionService(
                            stage_batch=stage_batch,
                        )

                        service.deactivate_stage_equipment()

                except Exception as cleanup_exc:

                    self.stderr.write(
                        f"Stage {stage_batch.id} "
                        f"cleanup failed: {cleanup_exc}"
                    )

                self.stderr.write(
                    f"Stage {stage_batch.id} "
                    f"failed: {exc}"
                )

