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





import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from treatment_process.models import (
    StageBatch,
    StageBatchProcessExecution,
    StageBatchProcessEquipmentExecution,
)

from treatment_process.services.stage_controller import (
    StageExecutionService,
)


class Command(BaseCommand):

    help = (
        "Process waiting treatment stage "
        "equipment executions."
    )

    def handle(self, *args, **options):

        self.stdout.write(
            "Treatment process worker started."
        )

        while True:

            try:

                # -------------------------------------------------
                # First process equipment executions that are
                # waiting for their scheduled OFF time.
                # -------------------------------------------------

                self.process_waiting_equipment()

                # -------------------------------------------------
                # Then process stages that can continue.
                # -------------------------------------------------

                self.process_pending_stages()

            except Exception as exc:

                self.stderr.write(
                    f"Worker error: {exc}"
                )

            # -------------------------------------------------
            # IMPORTANT:
            #
            # This sleep is ONLY worker polling delay.
            #
            # It is NOT equipment duration.
            #
            # The worker checks approximately every 1 second.
            # -------------------------------------------------

            time.sleep(1)

    # =========================================================
    # PROCESS WAITING EQUIPMENT
    # =========================================================

    def process_waiting_equipment(self):

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
                "scheduled_at"
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

        stage_batch = None

        try:

            with transaction.atomic():

                # -------------------------------------------------
                # Lock execution record.
                # -------------------------------------------------

                equipment_execution = (
                    StageBatchProcessEquipmentExecution
                    .objects
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
                # Make sure scheduled time has arrived.
                # -------------------------------------------------

                if (
                    equipment_execution.scheduled_at
                    and timezone.now()
                    < equipment_execution.scheduled_at
                ):

                    return

                # -------------------------------------------------
                # Equipment should still be ON.
                #
                # If something else changed it meanwhile,
                # do not blindly turn it OFF.
                # -------------------------------------------------

                equipment.refresh_from_db()

                if equipment.current_state != "ON":

                    equipment_execution.fail_execution(
                        remarks=(
                            f"Equipment '{equipment.name}' "
                            "is no longer ON."
                        )
                    )

                    return

                # -------------------------------------------------
                # Turn equipment OFF.
                # -------------------------------------------------

                service = StageExecutionService(
                    stage_batch
                )

                service.turn_equipment_off(
                    equipment
                )

                # -------------------------------------------------
                # Complete the waiting equipment execution.
                # -------------------------------------------------

                equipment_execution.complete_execution(
                    state="OFF"
                )

            # -----------------------------------------------------
            # Continue process OUTSIDE transaction.
            # -----------------------------------------------------

            stage_batch.refresh_from_db(
                fields=["status"]
            )

            if stage_batch.status != "RUNNING":

                return

            service = StageExecutionService(
                stage_batch
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
                            stage_batch
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

    def process_pending_stages(self):

        running_stages = (
            StageBatch.objects
            .filter(
                status="RUNNING"
            )
            .order_by(
                "created_at"
            )
        )

        for stage_batch in running_stages:

            # -------------------------------------------------
            # If this stage has a WAITING equipment execution,
            # it is waiting for its scheduled time.
            #
            # Do not start another operation.
            # -------------------------------------------------

            has_waiting_equipment = (
                StageBatchProcessEquipmentExecution
                .objects
                .filter(
                    stage_batch_process_execution__stage_batch=stage_batch,
                    status="WAITING",
                )
                .exists()
            )

            if has_waiting_equipment:

                continue

            # -------------------------------------------------
            # Continue or start the stage.
            # -------------------------------------------------

            try:

                service = StageExecutionService(
                    stage_batch
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
                            stage_batch
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