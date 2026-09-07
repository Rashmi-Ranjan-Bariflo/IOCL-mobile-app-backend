# from django.db import transaction

# from treatment_process.models import (
#     StageBatch,
#     StageBatchProcessExecution,
# )


# class StageExecutionService:
#     """
#     Handles automatic execution of a TreatmentStage.

#     The API is responsible for creating and starting the StageBatch.

#     This service is responsible for:
#         - executing processes sequentially
#         - getting process equipment
#         - reading equipment current state
#         - changing equipment state
#         - updating process execution status
#         - completing/failing the StageBatch
#     """

#     def __init__(self, stage_batch):
#         self.stage_batch = stage_batch

#     def execute(self):
#         """
#         Execute all processes of the stage sequentially.
#         """

#         try:

#             # ---------------------------------------------------------
#             # Get all pending process executions
#             # in process sequence order.
#             # ---------------------------------------------------------

#             process_executions = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related("process")
#                 .prefetch_related("process__equipments")
#                 .order_by("process__sequence")
#             )

#             # ---------------------------------------------------------
#             # Execute one process at a time.
#             # ---------------------------------------------------------

#             for process_execution in process_executions:

#                 self.execute_process(process_execution)

#             # ---------------------------------------------------------
#             # All processes completed successfully.
#             # ---------------------------------------------------------

#             self.stage_batch.complete_batch()

#             return True

#         except Exception as exc:

#             # ---------------------------------------------------------
#             # If any process fails, fail the complete stage batch.
#             # ---------------------------------------------------------

#             self.stage_batch.fail_batch()

#             raise exc

#     def execute_process(self, process_execution):
#         """
#         Execute one TreatmentProcess.

#         Important:
#             The same equipment can be used by multiple processes.

#         Example:

#             Process 1 -> Valve
#             Process 2 -> Motor
#             Process 3 -> Valve

#         Process 3 will get the same Valve record again and
#         read its latest current_state.
#         """

#         process = process_execution.process

#         # ---------------------------------------------------------
#         # Start this process.
#         # ---------------------------------------------------------

#         process_execution.start_process()

#         try:

#             # -----------------------------------------------------
#             # Get equipment configured for this process.
#             # -----------------------------------------------------

#             equipments = list(
#                 process.equipments
#                 .filter(is_active=True)
#                 .select_related("equipment_type")
#             )

#             if not equipments:

#                 raise ValueError(
#                     f"No active equipment configured "
#                     f"for process '{process.name}'."
#                 )

#             # -----------------------------------------------------
#             # Execute each equipment configured for this process.
#             # -----------------------------------------------------

#             for equipment in equipments:

#                 self.execute_equipment(equipment)

#             # -----------------------------------------------------
#             # Process completed.
#             # -----------------------------------------------------

#             process_execution.complete_process()

#         except Exception as exc:

#             # -----------------------------------------------------
#             # Process failed.
#             # -----------------------------------------------------

#             process_execution.fail_process(
#                 remarks=str(exc)
#             )

#             raise

#     def execute_equipment(self, equipment):
#         """
#         Execute the required operation for one equipment.

#         The important point here is that we use the equipment's
#         existing current_state.

#         Example:

#             current_state = OFF
#                 ↓
#             operation requires ON
#                 ↓
#             change OFF -> ON

#         Later, if another process uses the same equipment:

#             current_state = ON
#                 ↓
#             operation requires OFF
#                 ↓
#             change ON -> OFF

#         The service does NOT automatically perform the opposite
#         operation after changing the state.
#         """

#         # ---------------------------------------------------------
#         # Validate equipment availability.
#         # ---------------------------------------------------------

#         if not equipment.is_active:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         if equipment.status in ["FAULT", "MAINTENANCE"]:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' "
#                 f"is currently {equipment.status}."
#             )

#         # ---------------------------------------------------------
#         # At this point we read the current state from Equipment.
#         # ---------------------------------------------------------

#         current_state = equipment.current_state

#         # ---------------------------------------------------------
#         # TODO:
#         #
#         # Determine the required operation from the existing
#         # process configuration.
#         #
#         # We are intentionally NOT adding an action field here.
#         #
#         # The actual ON/OFF decision must come from the process
#         # configuration that your project already uses.
#         # ---------------------------------------------------------

#         required_state = self.get_required_state(equipment)

#         # ---------------------------------------------------------
#         # If equipment is already in the required state,
#         # don't perform another state change.
#         # ---------------------------------------------------------

#         if current_state == required_state:
#             return

#         # ---------------------------------------------------------
#         # Change equipment state.
#         #
#         # This is only one state change.
#         #
#         # There is NO automatic reverse operation here.
#         # ---------------------------------------------------------

#         equipment.current_state = required_state

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "updated_at",
#             ]
#         )

#     def get_required_state(self, equipment):
#         """
#         Return the state required for the current process.

#         This method will be connected to the existing process
#         configuration once that configuration is confirmed.

#         It is kept separate so that the equipment state-changing
#         logic does not depend on how the operation is determined.
#         """

#         raise NotImplementedError(
#             "Required equipment operation is not configured yet."
#         )





# from django.db import transaction

# from treatment_process.models import (
#     StageBatch,
#     StageBatchProcessExecution,
# )


# class StageExecutionService:
#     """
#     Service responsible for automatic execution of a treatment stage.

#     The API is responsible for:
#         - validating the stage
#         - validating equipment
#         - creating StageBatch
#         - creating process execution records
#         - starting the StageBatch

#     This service is responsible for:
#         - executing processes sequentially
#         - executing equipment configured for each process
#         - changing equipment state
#         - updating process execution status
#         - completing or failing the StageBatch
#     """

#     def __init__(self, stage_batch):
#         print("-----------------------------------------------------------------------------------------------")
#         self.stage_batch = stage_batch

#     # =====================================================================
#     # STAGE EXECUTION
#     # =====================================================================

#     def execute(self):
#         """
#         Execute all processes of the stage sequentially.

#         Example:

#             Process 1 -> Valve
#             Process 2 -> Motor
#             Process 3 -> Valve
#             Process 4 -> Motor

#         The processes are executed according to their sequence.

#         The same equipment can appear in multiple processes.

#         Example:

#             Process 1:
#                 Valve OFF -> ON

#             Process 3:
#                 Valve ON -> OFF
#         """

#         try:

#             # -------------------------------------------------------------
#             # Get all process executions belonging to this stage batch.
#             #
#             # We execute only PENDING processes.
#             # -------------------------------------------------------------

#             process_executions = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related("process")
#                 .prefetch_related(
#                     "process__equipments"
#                 )
#                 .order_by(
#                     "process__sequence"
#                 )
#             )

#             # -------------------------------------------------------------
#             # Execute processes one by one.
#             # -------------------------------------------------------------

#             for process_execution in process_executions:

#                 self.execute_process(
#                     process_execution
#                 )

#             # -------------------------------------------------------------
#             # All processes completed successfully.
#             # -------------------------------------------------------------

#             self.stage_batch.complete_batch()

#             # -------------------------------------------------------------
#             # Safety cleanup.
#             #
#             # After the complete stage finishes:
#             #
#             #     current_state = OFF
#             #     status        = INACTIVE
#             #
#             # -------------------------------------------------------------

#             self.deactivate_stage_equipment()

#             return True

#         except Exception as exc:

#             # -------------------------------------------------------------
#             # If any process fails, mark the stage batch as failed.
#             # -------------------------------------------------------------

#             self.stage_batch.fail_batch()

#             # -------------------------------------------------------------
#             # Safety cleanup.
#             # -------------------------------------------------------------

#             self.deactivate_stage_equipment()

#             raise exc

#     # =====================================================================
#     # PROCESS EXECUTION
#     # =====================================================================

#     def execute_process(self, process_execution):
#         """
#         Execute one process.

#         Process flow:

#             Process
#                 ↓
#             Get equipment
#                 ↓
#             Read current_state
#                 ↓
#             OFF -> ON
#             ON  -> OFF
#                 ↓
#             Process completed

#         Important:

#         We do NOT turn the equipment back automatically.

#         Example:

#             Process 1 -> Valve

#             Valve is OFF
#                 ↓
#             Valve becomes ON
#                 ↓
#             Process 1 completed

#         If Valve appears again:

#             Process 3 -> Valve

#             Valve is ON
#                 ↓
#             Valve becomes OFF
#                 ↓
#             Process 3 completed
#         """

#         process = process_execution.process

#         # -------------------------------------------------------------
#         # Mark process as RUNNING.
#         # -------------------------------------------------------------

#         process_execution.start_process()

#         try:

#             # ---------------------------------------------------------
#             # Get all equipment configured for this process.
#             # ---------------------------------------------------------

#             equipments = list(
#                 process.equipments
#                 .filter(
#                     is_active=True
#                 )
#                 .select_related(
#                     "equipment_type"
#                 )
#             )

#             # ---------------------------------------------------------
#             # A process must have at least one equipment.
#             # ---------------------------------------------------------

#             if not equipments:

#                 raise ValueError(
#                     f"No active equipment configured "
#                     f"for process '{process.name}'."
#                 )

#             # ---------------------------------------------------------
#             # Execute equipment one by one.
#             # ---------------------------------------------------------

#             for equipment in equipments:

#                 self.execute_equipment(
#                     equipment
#                 )

#             # ---------------------------------------------------------
#             # Process completed.
#             # ---------------------------------------------------------

#             process_execution.complete_process()

#         except Exception as exc:

#             # ---------------------------------------------------------
#             # Process failed.
#             # ---------------------------------------------------------

#             process_execution.fail_process(
#                 remarks=str(exc)
#             )

#             raise

#     # =====================================================================
#     # EQUIPMENT EXECUTION
#     # =====================================================================

#     def execute_equipment(self, equipment):
#         """
#         Execute one operation on an equipment.

#         The equipment's existing current_state determines the
#         state transition.

#             OFF -> ON
#             ON  -> OFF

#         The state is NOT stored on TreatmentProcess.

#         The current state always comes from the Equipment record.

#         This allows the same equipment to be used in multiple
#         processes.

#         Example:

#             Process 1 -> Valve

#                 Valve.current_state = OFF

#                 OFF -> ON


#             Process 2 -> Motor

#                 Motor.current_state = OFF

#                 OFF -> ON


#             Process 3 -> Valve

#                 Valve.current_state = ON

#                 ON -> OFF
#         """

#         # -------------------------------------------------------------
#         # Validate equipment master status.
#         # -------------------------------------------------------------

#         if not equipment.is_active:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         # -------------------------------------------------------------
#         # Equipment in FAULT or MAINTENANCE cannot be operated.
#         # -------------------------------------------------------------

#         if equipment.status in [
#             "FAULT",
#             "MAINTENANCE",
#         ]:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' "
#                 f"is currently {equipment.status}."
#             )

#         # -------------------------------------------------------------
#         # Read the CURRENT equipment state.
#         #
#         # This is the important part.
#         # -------------------------------------------------------------

#         current_state = equipment.current_state

#         # -------------------------------------------------------------
#         # OFF -> ON
#         # -------------------------------------------------------------

#         if current_state == "OFF":

#             equipment.current_state = "ON"

#         # -------------------------------------------------------------
#         # ON -> OFF
#         # -------------------------------------------------------------

#         elif current_state == "ON":

#             equipment.current_state = "OFF"

#         # -------------------------------------------------------------
#         # Invalid state.
#         # -------------------------------------------------------------

#         else:

#             raise ValueError(
#                 f"Invalid current state "
#                 f"'{current_state}' for equipment "
#                 f"'{equipment.name}'."
#             )

#         # -------------------------------------------------------------
#         # Save the new state.
#         # -------------------------------------------------------------

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "updated_at",
#             ]
#         )

#     # =====================================================================
#     # STAGE EQUIPMENT CLEANUP
#     # =====================================================================

#     def deactivate_stage_equipment(self):
#         """
#         Safely deactivate all equipment belonging to the stage.

#         Final stage state:

#             current_state = OFF
#             status        = INACTIVE

#         This is a stage-level safety cleanup.

#         It is NOT part of an individual process.
#         """

#         stage = self.stage_batch.stage

#         # -------------------------------------------------------------
#         # Get active stage equipment.
#         # -------------------------------------------------------------

#         equipments = stage.equipments.filter(
#             is_active=True
#         )

#         # -------------------------------------------------------------
#         # Turn everything OFF and make it INACTIVE.
#         # -------------------------------------------------------------

#         equipments.update(
#             current_state="OFF",
#             status="INACTIVE",
#         )





import time

from datetime import datetime, timedelta

from django.utils import timezone

from treatment_process.models import (
    StageBatchProcessExecution,
)


# class StageExecutionService:
#     """
#     Executes all processes of a StageBatch sequentially.

#     Main rules:

#     1. Processes execute according to their sequence.

#     2. Process.equipments defines which equipment the process uses.

#     3. Equipment.current_state determines the next operation:
#            OFF -> ON
#            ON  -> OFF

#     4. Equipment.duration_seconds determines whether the equipment
#        requires timing.

#     5. Equipment without duration works as normal ON/OFF equipment.

#     6. Equipment with duration is timing-enabled.

#     7. When timing-enabled equipment is turned ON:
#            - start_time is recorded.

#     8. When the same timing-enabled equipment is requested to turn OFF:
#            - elapsed time is calculated.
#            - if duration is not completed, execution waits.
#            - after duration is completed, equipment is turned OFF.

#     9. No equipment-type-specific logic is used.

#     10. At the end of the complete stage:
#             current_state = OFF
#             status = INACTIVE
#     """

#     def __init__(self, stage_batch):
#         self.stage_batch = stage_batch

#     # =========================================================
#     # EXECUTE COMPLETE STAGE
#     # =========================================================

#     def execute(self):
#         try:

#             # -------------------------------------------------
#             # Get all pending processes in sequence order.
#             # -------------------------------------------------
#             process_executions = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related("process")
#                 .prefetch_related("process__equipments")
#                 .order_by("process__sequence")
#             )

#             # -------------------------------------------------
#             # Execute processes one by one.
#             # -------------------------------------------------
#             for process_execution in process_executions:
#                 self.execute_process(process_execution)

#             # -------------------------------------------------
#             # All processes completed.
#             # -------------------------------------------------
#             self.stage_batch.complete_batch()

#             # -------------------------------------------------
#             # After the complete stage:
#             #
#             # All stage equipment becomes:
#             #
#             #     current_state = OFF
#             #     status = INACTIVE
#             # -------------------------------------------------
#             self.deactivate_stage_equipment()

#             return True

#         except Exception as exc:

#             # -------------------------------------------------
#             # If any process fails, fail the complete batch.
#             # -------------------------------------------------
#             self.stage_batch.fail_batch()

#             # -------------------------------------------------
#             # Safety state.
#             # -------------------------------------------------
#             self.deactivate_stage_equipment()

#             raise exc

#     # =========================================================
#     # EXECUTE ONE PROCESS
#     # =========================================================

#     def execute_process(self, process_execution):

#         process = process_execution.process

#         # -----------------------------------------------------
#         # Mark process as running.
#         # -----------------------------------------------------
#         process_execution.start_process()

#         try:

#             # -------------------------------------------------
#             # Process equipment comes ONLY from:
#             #
#             #     TreatmentProcess.equipments
#             #
#             # We do not use stage.equipments here.
#             # -------------------------------------------------
#             equipments = list(
#                 process.equipments
#                 .filter(is_active=True)
#                 .select_related("equipment_type")
#                 .all()
#             )

#             # -------------------------------------------------
#             # Every process must have equipment configured.
#             # -------------------------------------------------
#             if not equipments:
#                 raise ValueError(
#                     f"No equipment configured for process "
#                     f"'{process.name}'."
#                 )

#             # -------------------------------------------------
#             # Execute each equipment configured for this process.
#             # -------------------------------------------------
#             for equipment in equipments:
#                 self.execute_equipment(equipment)

#             # -------------------------------------------------
#             # Process completed.
#             # -------------------------------------------------
#             process_execution.complete_process()

#         except Exception as exc:

#             # -------------------------------------------------
#             # Mark process as failed.
#             # -------------------------------------------------
#             process_execution.fail_process(
#                 remarks=str(exc)
#             )

#             raise

#     # =========================================================
#     # EXECUTE EQUIPMENT
#     # =========================================================

#     def execute_equipment(self, equipment):

#         # -----------------------------------------------------
#         # Validate equipment.
#         # -----------------------------------------------------

#         if not equipment.is_active:
#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         if equipment.status in [
#             "FAULT",
#             "MAINTENANCE",
#         ]:
#             raise ValueError(
#                 f"Equipment '{equipment.name}' is "
#                 f"{equipment.status}."
#             )

#         # =====================================================
#         # CASE 1: EQUIPMENT IS CURRENTLY OFF
#         # =====================================================

#         if equipment.current_state == "OFF":

#             self.turn_equipment_on(equipment)

#         # =====================================================
#         # CASE 2: EQUIPMENT IS CURRENTLY ON
#         # =====================================================

#         elif equipment.current_state == "ON":

#             self.turn_equipment_off(equipment)

#         # =====================================================
#         # INVALID STATE
#         # =====================================================

#         else:

#             raise ValueError(
#                 f"Invalid current state "
#                 f"'{equipment.current_state}' for equipment "
#                 f"'{equipment.name}'."
#             )

#     # =========================================================
#     # TURN EQUIPMENT ON
#     # =========================================================

#     def turn_equipment_on(self, equipment):

#         # -----------------------------------------------------
#         # Change equipment state to ON.
#         # -----------------------------------------------------
#         equipment.current_state = "ON"

#         # -----------------------------------------------------
#         # Check whether this equipment requires timing.
#         #
#         # duration_seconds = NULL
#         #     -> normal equipment
#         #
#         # duration_seconds has value
#         #     -> timing-enabled equipment
#         # -----------------------------------------------------

#         if equipment.duration_seconds is not None:

#             # -------------------------------------------------
#             # Record the time at which the equipment
#             # became ON.
#             #
#             # Your model currently uses TimeField, so we
#             # continue using time().
#             # -------------------------------------------------
#             equipment.start_time = timezone.now().time()

#             # -------------------------------------------------
#             # Clear previous end time because a new ON cycle
#             # has started.
#             # -------------------------------------------------
#             equipment.end_time = None

#             print(
#                 f"Equipment ON with timing: "
#                 f"{equipment.name} "
#                 f"({equipment.duration_seconds} seconds)"
#             )

#         else:

#             # -------------------------------------------------
#             # Normal equipment.
#             #
#             # No timing is required.
#             # -------------------------------------------------
#             print(
#                 f"Equipment ON without timing: "
#                 f"{equipment.name}"
#             )

#         # -----------------------------------------------------
#         # Save the equipment state.
#         # -----------------------------------------------------
#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "start_time",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#     # =========================================================
#     # TURN EQUIPMENT OFF
#     # =========================================================

#     def turn_equipment_off(self, equipment):

#         # =====================================================
#         # CASE 1: NO TIMING CONFIGURED
#         # =====================================================

#         if equipment.duration_seconds is None:

#             # -------------------------------------------------
#             # No duration means the equipment can be turned OFF
#             # immediately.
#             # -------------------------------------------------
#             print(
#                 f"Equipment OFF without timing: "
#                 f"{equipment.name}"
#             )

#             equipment.current_state = "OFF"
#             equipment.end_time = timezone.now().time()

#             equipment.save(
#                 update_fields=[
#                     "current_state",
#                     "end_time",
#                     "updated_at",
#                 ]
#             )

#             return

#         # =====================================================
#         # CASE 2: TIMING CONFIGURED
#         # =====================================================

#         print(
#             f"Equipment OFF requested with timing: "
#             f"{equipment.name} "
#             f"({equipment.duration_seconds} seconds)"
#         )

#         # -----------------------------------------------------
#         # Check whether the required duration has completed.
#         # -----------------------------------------------------
#         self.wait_for_duration(equipment)

#         # -----------------------------------------------------
#         # Required duration is now complete.
#         # -----------------------------------------------------
#         equipment.current_state = "OFF"
#         equipment.end_time = timezone.now().time()

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#         print(
#             f"Equipment OFF after duration completed: "
#             f"{equipment.name}"
#         )

#     # =========================================================
#     # WAIT FOR EQUIPMENT DURATION
#     # =========================================================

#     def wait_for_duration(self, equipment):

#         # -----------------------------------------------------
#         # If there is no duration, there is nothing to wait for.
#         # -----------------------------------------------------
#         if equipment.duration_seconds is None:
#             return

#         # -----------------------------------------------------
#         # We need start_time to calculate elapsed time.
#         # -----------------------------------------------------
#         if equipment.start_time is None:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' has duration "
#                 f"configured but start_time is missing."
#             )

#         duration_seconds = equipment.duration_seconds

#         # -----------------------------------------------------
#         # Convert the stored TimeField into a datetime.
#         #
#         # We use today's date because the current ON cycle
#         # started during the current execution.
#         # -----------------------------------------------------
#         now = timezone.now()

#         start_datetime = timezone.make_aware(
#             datetime.combine(
#                 now.date(),
#                 equipment.start_time,
#             ),
#             timezone.get_current_timezone(),
#         )

#         # -----------------------------------------------------
#         # Calculate elapsed time.
#         # -----------------------------------------------------
#         elapsed_seconds = (
#             timezone.now() - start_datetime
#         ).total_seconds()

#         # -----------------------------------------------------
#         # Handle the case where the stored start_time is from
#         # just before midnight and the current time is after
#         # midnight.
#         # -----------------------------------------------------
#         if elapsed_seconds < 0:

#             start_datetime = start_datetime - timedelta(days=1)

#             elapsed_seconds = (
#                 timezone.now() - start_datetime
#             ).total_seconds()

#         # -----------------------------------------------------
#         # Calculate how much time is still remaining.
#         # -----------------------------------------------------
#         remaining_seconds = (
#             duration_seconds - elapsed_seconds
#         )

#         print(
#             f"Equipment '{equipment.name}' timing check:"
#         )

#         print(
#             f"Required duration: "
#             f"{duration_seconds} seconds"
#         )

#         print(
#             f"Elapsed duration: "
#             f"{round(elapsed_seconds, 2)} seconds"
#         )

#         print(
#             f"Remaining duration: "
#             f"{round(max(remaining_seconds, 0), 2)} seconds"
#         )

#         # =====================================================
#         # DURATION ALREADY COMPLETED
#         # =====================================================

#         if remaining_seconds <= 0:

#             print(
#                 f"Equipment '{equipment.name}' duration "
#                 f"is already completed."
#             )

#             return

#         # =====================================================
#         # DURATION NOT COMPLETED
#         # =====================================================

#         print(
#             f"Equipment '{equipment.name}' must remain ON "
#             f"for another {round(remaining_seconds, 2)} seconds."
#         )

#         # -----------------------------------------------------
#         # Wait until the configured duration is completed.
#         #
#         # We use small intervals instead of sleeping for the
#         # complete duration at once.
#         #
#         # This allows us to check the remaining time repeatedly.
#         # -----------------------------------------------------
#         while remaining_seconds > 0:

#             # -------------------------------------------------
#             # Wait only a small amount at a time.
#             #
#             # This avoids one very large sleep operation.
#             # -------------------------------------------------
#             sleep_seconds = min(
#                 remaining_seconds,
#                 0.5,
#             )

#             time.sleep(sleep_seconds)

#             # -------------------------------------------------
#             # Recalculate elapsed time.
#             # -------------------------------------------------
#             elapsed_seconds = (
#                 timezone.now() - start_datetime
#             ).total_seconds()

#             remaining_seconds = (
#                 duration_seconds - elapsed_seconds
#             )

#         print(
#             f"Equipment '{equipment.name}' duration completed."
#         )

#     # =========================================================
#     # DEACTIVATE STAGE EQUIPMENT
#     # =========================================================

#     def deactivate_stage_equipment(self):

#         stage = self.stage_batch.stage

#         # -----------------------------------------------------
#         # At the end of the stage:
#         #
#         # current_state -> OFF
#         # status         -> INACTIVE
#         #
#         # This is the final safety state of the stage.
#         # -----------------------------------------------------

#         stage.equipments.filter(
#             is_active=True
#         ).update(
#             current_state="OFF",
#             status="INACTIVE",
#         )





# import time

# from datetime import datetime, timedelta

# from django.utils import timezone

# from treatment_process.models import (
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )


# class StageExecutionService:
#     """
#     Executes all processes of a StageBatch sequentially.

#     Main rules:

#     1. Processes execute according to their sequence.

#     2. Process.equipments defines which equipment the process uses.

#     3. Equipment.current_state determines the next operation:
#            OFF -> ON
#            ON  -> OFF

#     4. Equipment.duration_seconds determines whether the
#        equipment requires timing.

#     5. Equipment without duration works immediately.

#     6. Equipment with duration waits until the configured
#        duration has completed before turning OFF.

#     7. Every process/equipment combination is recorded in:
#            StageBatchProcessEquipmentExecution

#     8. Equipment.current_state represents the current/global
#        equipment state.

#     9. The equipment execution record represents the state
#        produced by that specific process.

#     10. At the end of the complete stage:
#             current_state = OFF
#             status = INACTIVE
#     """

#     def __init__(self, stage_batch):
#         self.stage_batch = stage_batch

#     # =========================================================
#     # EXECUTE COMPLETE STAGE
#     # =========================================================

#     def execute(self):

#         try:

#             # -------------------------------------------------
#             # Get all pending processes in sequence order.
#             # -------------------------------------------------

#             process_executions = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related(
#                     "process",
#                 )
#                 .prefetch_related(
#                     "process__equipments",
#                 )
#                 .order_by(
#                     "process__sequence",
#                 )
#             )

#             # -------------------------------------------------
#             # Execute processes one by one.
#             # -------------------------------------------------

#             for process_execution in process_executions:

#                 self.execute_process(
#                     process_execution
#                 )

#             # -------------------------------------------------
#             # All processes completed.
#             # -------------------------------------------------

#             self.stage_batch.complete_batch()

#             # -------------------------------------------------
#             # Final safety state.
#             # -------------------------------------------------

#             self.deactivate_stage_equipment()

#             return True

#         except Exception as exc:

#             # -------------------------------------------------
#             # If any process fails, fail the complete batch.
#             # -------------------------------------------------

#             self.stage_batch.fail_batch()

#             # -------------------------------------------------
#             # Final safety state.
#             # -------------------------------------------------

#             self.deactivate_stage_equipment()

#             raise exc

#     # =========================================================
#     # EXECUTE ONE PROCESS
#     # =========================================================

#     def execute_process(self, process_execution):

#         process = process_execution.process

#         # -----------------------------------------------------
#         # Mark process as running.
#         # -----------------------------------------------------

#         process_execution.start_process()

#         try:

#             # -------------------------------------------------
#             # Get equipment configured for this process.
#             #
#             # IMPORTANT:
#             #
#             # We use TreatmentProcess.equipments.
#             #
#             # We do NOT use stage.equipments here.
#             # -------------------------------------------------

#             equipments = list(
#                 process.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .select_related(
#                     "equipment_type",
#                 )
#                 .all()
#             )

#             # -------------------------------------------------
#             # Every process must have equipment.
#             # -------------------------------------------------

#             if not equipments:

#                 raise ValueError(
#                     f"No equipment configured for process "
#                     f"'{process.name}'."
#                 )

#             # -------------------------------------------------
#             # Execute each equipment.
#             # -------------------------------------------------

#             for equipment in equipments:

#                 self.execute_equipment(
#                     process_execution,
#                     equipment,
#                 )

#             # -------------------------------------------------
#             # Process completed.
#             # -------------------------------------------------

#             process_execution.complete_process()

#         except Exception as exc:

#             # -------------------------------------------------
#             # Process failed.
#             # -------------------------------------------------

#             process_execution.fail_process(
#                 remarks=str(exc)
#             )

#             raise

#     # =========================================================
#     # EXECUTE EQUIPMENT
#     # =========================================================

#     def execute_equipment(
#         self,
#         process_execution,
#         equipment,
#     ):

#         # -----------------------------------------------------
#         # Validate equipment.
#         # -----------------------------------------------------

#         if not equipment.is_active:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         if equipment.status in [
#             "FAULT",
#             "MAINTENANCE",
#         ]:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is "
#                 f"{equipment.status}."
#             )

#         # -----------------------------------------------------
#         # Create equipment execution record.
#         #
#         # This record belongs specifically to this process.
#         # -----------------------------------------------------

#         equipment_execution = (
#             StageBatchProcessEquipmentExecution.objects.create(
#                 stage_batch_process_execution=process_execution,
#                 equipment=equipment,
#                 state=None,
#             )
#         )

#         # -----------------------------------------------------
#         # Mark equipment execution as started.
#         # -----------------------------------------------------

#         equipment_execution.start_execution()

#         try:

#             # =================================================
#             # EQUIPMENT CURRENTLY OFF
#             # =================================================

#             if equipment.current_state == "OFF":

#                 self.turn_equipment_on(
#                     equipment
#                 )

#             # =================================================
#             # EQUIPMENT CURRENTLY ON
#             # =================================================

#             elif equipment.current_state == "ON":

#                 self.turn_equipment_off(
#                     equipment
#                 )

#             # =================================================
#             # INVALID STATE
#             # =================================================

#             else:

#                 raise ValueError(
#                     f"Invalid current state "
#                     f"'{equipment.current_state}' for equipment "
#                     f"'{equipment.name}'."
#                 )

#             # -------------------------------------------------
#             # IMPORTANT:
#             #
#             # After the equipment operation has completed,
#             # read the actual current state.
#             #
#             # Example:
#             #
#             # OFF -> ON
#             #     => store ON
#             #
#             # ON -> OFF
#             #     => store OFF
#             # -------------------------------------------------

#             equipment_execution.complete_execution(
#                 state=equipment.current_state
#             )

#         except Exception:

#             # -------------------------------------------------
#             # We intentionally do not mark the equipment
#             # execution as completed if the operation fails.
#             # -------------------------------------------------

#             raise

#     # =========================================================
#     # TURN EQUIPMENT ON
#     # =========================================================

#     def turn_equipment_on(self, equipment):

#         # -----------------------------------------------------
#         # Change equipment state to ON.
#         # -----------------------------------------------------

#         equipment.current_state = "ON"

#         # -----------------------------------------------------
#         # Timing-enabled equipment.
#         # -----------------------------------------------------

#         if equipment.duration_seconds is not None:

#             # -------------------------------------------------
#             # Record ON start time.
#             # -------------------------------------------------

#             equipment.start_time = timezone.now().time()

#             # -------------------------------------------------
#             # Clear previous end time.
#             # -------------------------------------------------

#             equipment.end_time = None

#             print(
#                 f"Equipment ON with timing: "
#                 f"{equipment.name} "
#                 f"({equipment.duration_seconds} seconds)"
#             )

#         else:

#             # -------------------------------------------------
#             # No timing.
#             # -------------------------------------------------

#             print(
#                 f"Equipment ON without timing: "
#                 f"{equipment.name}"
#             )

#         # -----------------------------------------------------
#         # Save equipment.
#         # -----------------------------------------------------

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "start_time",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#     # =========================================================
#     # TURN EQUIPMENT OFF
#     # =========================================================

#     def turn_equipment_off(self, equipment):

#         # =====================================================
#         # NO TIMING
#         # =====================================================

#         if equipment.duration_seconds is None:

#             print(
#                 f"Equipment OFF without timing: "
#                 f"{equipment.name}"
#             )

#             equipment.current_state = "OFF"

#             equipment.end_time = (
#                 timezone.now().time()
#             )

#             equipment.save(
#                 update_fields=[
#                     "current_state",
#                     "end_time",
#                     "updated_at",
#                 ]
#             )

#             return

#         # =====================================================
#         # TIMING ENABLED
#         # =====================================================

#         print(
#             f"Equipment OFF requested with timing: "
#             f"{equipment.name} "
#             f"({equipment.duration_seconds} seconds)"
#         )

#         # -----------------------------------------------------
#         # Wait until configured duration is completed.
#         # -----------------------------------------------------

#         self.wait_for_duration(
#             equipment
#         )

#         # -----------------------------------------------------
#         # Duration completed.
#         # -----------------------------------------------------

#         equipment.current_state = "OFF"

#         equipment.end_time = (
#             timezone.now().time()
#         )

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#         print(
#             f"Equipment OFF after duration completed: "
#             f"{equipment.name}"
#         )

#     # =========================================================
#     # WAIT FOR EQUIPMENT DURATION
#     # =========================================================

#     def wait_for_duration(self, equipment):

#         # -----------------------------------------------------
#         # No duration means no waiting.
#         # -----------------------------------------------------

#         if equipment.duration_seconds is None:

#             return

#         # -----------------------------------------------------
#         # start_time is required.
#         # -----------------------------------------------------

#         if equipment.start_time is None:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' has duration "
#                 f"configured but start_time is missing."
#             )

#         duration_seconds = (
#             equipment.duration_seconds
#         )

#         now = timezone.now()

#         # -----------------------------------------------------
#         # Convert TimeField into today's datetime.
#         # -----------------------------------------------------

#         start_datetime = timezone.make_aware(
#             datetime.combine(
#                 now.date(),
#                 equipment.start_time,
#             ),
#             timezone.get_current_timezone(),
#         )

#         # -----------------------------------------------------
#         # Calculate elapsed time.
#         # -----------------------------------------------------

#         elapsed_seconds = (
#             timezone.now() - start_datetime
#         ).total_seconds()

#         # -----------------------------------------------------
#         # Handle midnight crossing.
#         # -----------------------------------------------------

#         if elapsed_seconds < 0:

#             start_datetime = (
#                 start_datetime - timedelta(days=1)
#             )

#             elapsed_seconds = (
#                 timezone.now() - start_datetime
#             ).total_seconds()

#         # -----------------------------------------------------
#         # Calculate remaining time.
#         # -----------------------------------------------------

#         remaining_seconds = (
#             duration_seconds - elapsed_seconds
#         )

#         print(
#             f"Equipment '{equipment.name}' timing check:"
#         )

#         print(
#             f"Required duration: "
#             f"{duration_seconds} seconds"
#         )

#         print(
#             f"Elapsed duration: "
#             f"{round(elapsed_seconds, 2)} seconds"
#         )

#         print(
#             f"Remaining duration: "
#             f"{round(max(remaining_seconds, 0), 2)} seconds"
#         )

#         # =====================================================
#         # ALREADY COMPLETED
#         # =====================================================

#         if remaining_seconds <= 0:

#             print(
#                 f"Equipment '{equipment.name}' duration "
#                 f"is already completed."
#             )

#             return

#         # =====================================================
#         # WAIT
#         # =====================================================

#         print(
#             f"Equipment '{equipment.name}' must remain ON "
#             f"for another "
#             f"{round(remaining_seconds, 2)} seconds."
#         )

#         while remaining_seconds > 0:

#             # -------------------------------------------------
#             # Wait in small intervals.
#             # -------------------------------------------------

#             sleep_seconds = min(
#                 remaining_seconds,
#                 0.5,
#             )

#             time.sleep(
#                 sleep_seconds
#             )

#             # -------------------------------------------------
#             # Recalculate elapsed time.
#             # -------------------------------------------------

#             elapsed_seconds = (
#                 timezone.now() - start_datetime
#             ).total_seconds()

#             remaining_seconds = (
#                 duration_seconds - elapsed_seconds
#             )

#         print(
#             f"Equipment '{equipment.name}' duration completed."
#         )

#     # =========================================================
#     # DEACTIVATE STAGE EQUIPMENT
#     # =========================================================

#     def deactivate_stage_equipment(self):

#         stage = self.stage_batch.stage

#         # -----------------------------------------------------
#         # Final safety state.
#         #
#         # All stage equipment:
#         #
#         #     current_state = OFF
#         #     status = INACTIVE
#         # -----------------------------------------------------

#         stage.equipments.filter(
#             is_active=True,
#         ).update(
#             current_state="OFF",
#             status="INACTIVE",
#         )






# from django.db import transaction
# from django.utils import timezone
# from datetime import timedelta

# from treatment_process.models import (
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )


# class StageExecutionService:
#     """
#     Executes a TreatmentStage without blocking the server.

#     Main rules:

#     1. Processes execute according to sequence.

#     2. Process.equipments defines which equipment
#        belongs to the process.

#     3. Equipment.current_state determines the
#        next operation:

#            OFF -> ON
#            ON  -> OFF

#     4. Equipment.duration_seconds determines whether
#        timing is required.

#     5. Equipment without duration executes immediately.

#     6. Equipment with duration:

#            ON
#            ↓
#            store scheduled_at
#            ↓
#            return

#        The service DOES NOT wait.

#     7. A background worker later finds the WAITING
#        equipment execution when scheduled_at is reached.

#     8. After the timed operation is completed,
#        the next process can continue.

#     9. Different stages can execute independently.

#     10. No time.sleep() is used.
#     """

#     def __init__(self, stage_batch):
#         self.stage_batch = stage_batch

#     # =========================================================
#     # EXECUTE COMPLETE STAGE
#     # =========================================================

#     def execute(self):

#         try:

#             process_execution = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related("process")
#                 .prefetch_related("process__equipments")
#                 .order_by("process__sequence")
#                 .first()
#             )

#             if not process_execution:

#                 self.stage_batch.complete_batch()

#                 self.deactivate_stage_equipment()

#                 return True

#             result = self.execute_process(
#                 process_execution
#             )

#             return result

#         except Exception as exc:

#             self.stage_batch.fail_batch()

#             self.deactivate_stage_equipment()

#             raise exc

#     # =========================================================
#     # EXECUTE ONE PROCESS
#     # =========================================================

#     def execute_process(self, process_execution):

#         process = process_execution.process

#         process_execution.start_process()

#         try:

#             equipments = list(
#                 process.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .select_related(
#                     "equipment_type",
#                 )
#                 .all()
#             )

#             if not equipments:

#                 raise ValueError(
#                     f"No equipment configured for process "
#                     f"'{process.name}'."
#                 )

#             # -------------------------------------------------
#             # Execute equipment one by one.
#             # -------------------------------------------------

#             for equipment in equipments:

#                 result = self.execute_equipment(
#                     process_execution,
#                     equipment,
#                 )

#                 # -------------------------------------------------
#                 # If equipment needs to wait, stop here.
#                 #
#                 # We DO NOT continue to the next process.
#                 # -------------------------------------------------

#                 if result == "WAITING":

#                     return "WAITING"

#             # -------------------------------------------------
#             # All equipment operations completed.
#             # -------------------------------------------------

#             process_execution.complete_process()

#             # -------------------------------------------------
#             # Try to continue the stage.
#             # -------------------------------------------------

#             return self.execute()

#         except Exception as exc:

#             process_execution.fail_process(
#                 remarks=str(exc)
#             )

#             raise

#     # =========================================================
#     # EXECUTE EQUIPMENT
#     # =========================================================

#     def execute_equipment(
#         self,
#         process_execution,
#         equipment,
#     ):

#         # -----------------------------------------------------
#         # Validate equipment.
#         # -----------------------------------------------------

#         if not equipment.is_active:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         if equipment.status in [
#             "FAULT",
#             "MAINTENANCE",
#         ]:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is "
#                 f"{equipment.status}."
#             )

#         # -----------------------------------------------------
#         # Create equipment execution record.
#         # -----------------------------------------------------

#         equipment_execution = (
#             StageBatchProcessEquipmentExecution.objects.create(
#                 stage_batch_process_execution=process_execution,
#                 equipment=equipment,
#                 state=None,
#             )
#         )

#         equipment_execution.start_execution()

#         try:

#             # =================================================
#             # EQUIPMENT OFF
#             # =================================================

#             if equipment.current_state == "OFF":

#                 self.turn_equipment_on(
#                     equipment,
#                 )

#                 equipment_execution.complete_execution(
#                     state="ON",
#                 )

#                 # -------------------------------------------------
#                 # Important:
#                 #
#                 # Turning ON with duration does NOT mean
#                 # the process is finished.
#                 #
#                 # We schedule the next check.
#                 # -------------------------------------------------

#                 if equipment.duration_seconds is not None:

#                     scheduled_at = (
#                         timezone.now()
#                         + timedelta(
#                             seconds=equipment.duration_seconds
#                         )
#                     )

#                     equipment_execution.wait_execution(
#                         scheduled_at
#                     )

#                     print(
#                         f"{equipment.name} is ON."
#                     )

#                     print(
#                         f"Next action scheduled at: "
#                         f"{scheduled_at}"
#                     )

#                     return "WAITING"

#                 return "COMPLETED"

#             # =================================================
#             # EQUIPMENT ON
#             # =================================================

#             elif equipment.current_state == "ON":

#                 # -------------------------------------------------
#                 # If duration is configured, we need to determine
#                 # whether the required time has completed.
#                 # -------------------------------------------------

#                 if equipment.duration_seconds is not None:

#                     if equipment.start_time is None:

#                         raise ValueError(
#                             f"Equipment '{equipment.name}' has "
#                             f"duration configured but start_time "
#                             f"is missing."
#                         )

#                     if not self.is_duration_completed(
#                         equipment
#                     ):

#                         scheduled_at = (
#                             self.get_scheduled_time(
#                                 equipment
#                             )
#                         )

#                         equipment_execution.wait_execution(
#                             scheduled_at
#                         )

#                         print(
#                             f"{equipment.name} is still ON."
#                         )

#                         print(
#                             f"Next check at: "
#                             f"{scheduled_at}"
#                         )

#                         return "WAITING"

#                 # -------------------------------------------------
#                 # Duration completed or no duration.
#                 # -------------------------------------------------

#                 self.turn_equipment_off(
#                     equipment
#                 )

#                 equipment_execution.complete_execution(
#                     state="OFF",
#                 )

#                 return "COMPLETED"

#             else:

#                 raise ValueError(
#                     f"Invalid current state "
#                     f"'{equipment.current_state}' for "
#                     f"equipment '{equipment.name}'."
#                 )

#         except Exception as exc:

#             equipment_execution.fail_execution(
#                 remarks=str(exc)
#             )

#             raise

#     # =========================================================
#     # TURN EQUIPMENT ON
#     # =========================================================

#     def turn_equipment_on(
#         self,
#         equipment,
#     ):

#         equipment.current_state = "ON"

#         # -----------------------------------------------------
#         # Timing equipment.
#         # -----------------------------------------------------

#         if equipment.duration_seconds is not None:

#             equipment.start_time = (
#                 timezone.now().time()
#             )

#             equipment.end_time = None

#             print(
#                 f"Equipment ON with timing: "
#                 f"{equipment.name} "
#                 f"({equipment.duration_seconds} seconds)"
#             )

#         else:

#             print(
#                 f"Equipment ON without timing: "
#                 f"{equipment.name}"
#             )

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "start_time",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#     # =========================================================
#     # TURN EQUIPMENT OFF
#     # =========================================================

#     def turn_equipment_off(
#         self,
#         equipment,
#     ):

#         equipment.current_state = "OFF"

#         equipment.end_time = (
#             timezone.now().time()
#         )

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#         print(
#             f"Equipment OFF: "
#             f"{equipment.name}"
#         )

#     # =========================================================
#     # CHECK DURATION
#     # =========================================================

#     def is_duration_completed(
#         self,
#         equipment,
#     ):

#         if equipment.duration_seconds is None:

#             return True

#         if equipment.start_time is None:

#             return False

#         scheduled_at = (
#             self.get_scheduled_time(
#                 equipment
#             )
#         )

#         return timezone.now() >= scheduled_at

#     # =========================================================
#     # GET SCHEDULED TIME
#     # =========================================================

#     def get_scheduled_time(
#         self,
#         equipment,
#     ):

#         now = timezone.now()

#         start_datetime = timezone.make_aware(
#             timezone.datetime.combine(
#                 now.date(),
#                 equipment.start_time,
#             ),
#             timezone.get_current_timezone(),
#         )

#         # -----------------------------------------------------
#         # Handle midnight crossing.
#         # -----------------------------------------------------

#         if start_datetime > now:

#             start_datetime -= timedelta(
#                 days=1
#             )

#         scheduled_at = (
#             start_datetime
#             + timedelta(
#                 seconds=equipment.duration_seconds
#             )
#         )

#         return scheduled_at

#     # =========================================================
#     # DEACTIVATE STAGE EQUIPMENT
#     # =========================================================

#     def deactivate_stage_equipment(self):

#         stage = self.stage_batch.stage

#         stage.equipments.filter(
#             is_active=True,
#         ).update(
#             current_state="OFF",
#             status="INACTIVE",
#         )





# from django.db import transaction
# from django.utils import timezone
# from datetime import timedelta

# from treatment_process.models import (
#     StageBatchProcessExecution,
#     StageBatchProcessEquipmentExecution,
# )


# class StageExecutionService:
#     """
#     Executes a TreatmentStage without blocking the server.

#     Main rules:

#     1. Processes execute according to sequence.

#     2. Process.equipments defines which equipment
#        belongs to the process.

#     3. Equipment.current_state determines the
#        next operation:

#            OFF -> ON
#            ON  -> OFF

#     4. Equipment.duration_seconds determines whether
#        timing is required.

#     5. Equipment without duration executes immediately.

#     6. Equipment with duration:

#            ON
#            ↓
#            create equipment execution
#            ↓
#            WAITING
#            ↓
#            scheduled_at
#            ↓
#            worker checks later
#            ↓
#            OFF

#     7. The service DOES NOT wait for equipment duration.

#     8. A process remains RUNNING while one of its
#        equipment executions is WAITING.

#     9. After the timed equipment is completed,
#        the same process continues from the next
#        equipment.

#     10. After all equipment of the process are completed,
#         the next process starts.

#     11. Different stages can execute independently.

#     12. STOPPED batches must never continue execution.

#     13. No equipment-duration time.sleep() is used.
#     """

#     def __init__(self, stage_batch):
#         self.stage_batch = stage_batch

#     # =========================================================
#     # EXECUTE STAGE
#     # =========================================================

#     def execute(self):

#         try:

#             # -------------------------------------------------
#             # IMPORTANT:
#             #
#             # A stopped / completed / failed batch must never
#             # continue execution.
#             # -------------------------------------------------

#             if self.stage_batch.status != "RUNNING":

#                 return self.stage_batch.status

#             # -------------------------------------------------
#             # First check whether there is already a RUNNING
#             # process.
#             #
#             # This is important when a timed equipment execution
#             # has completed and the same process needs to continue.
#             # -------------------------------------------------

#             running_process_execution = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="RUNNING",
#                 )
#                 .select_related("process")
#                 .first()
#             )

#             if running_process_execution:

#                 return self.execute_process(
#                     running_process_execution
#                 )

#             # -------------------------------------------------
#             # Find next PENDING process.
#             # -------------------------------------------------

#             process_execution = (
#                 StageBatchProcessExecution.objects
#                 .filter(
#                     stage_batch=self.stage_batch,
#                     status="PENDING",
#                 )
#                 .select_related("process")
#                 .prefetch_related("process__equipments")
#                 .order_by("process__sequence")
#                 .first()
#             )

#             # -------------------------------------------------
#             # No PENDING process means the stage is complete.
#             # -------------------------------------------------

#             if not process_execution:

#                 self.stage_batch.complete_batch()

#                 self.deactivate_stage_equipment()

#                 return True

#             # -------------------------------------------------
#             # Execute the process.
#             # -------------------------------------------------

#             return self.execute_process(
#                 process_execution
#             )

#         except Exception as exc:

#             # -------------------------------------------------
#             # Do not overwrite STOPPED with FAILED.
#             # -------------------------------------------------

#             if self.stage_batch.status == "RUNNING":

#                 self.stage_batch.fail_batch()

#                 self.deactivate_stage_equipment()

#             raise exc

#     # =========================================================
#     # EXECUTE ONE PROCESS
#     # =========================================================

#     def execute_process(self, process_execution):

#         # -----------------------------------------------------
#         # A stopped batch must not continue.
#         # -----------------------------------------------------

#         if self.stage_batch.status != "RUNNING":

#             return self.stage_batch.status

#         process = process_execution.process

#         # -----------------------------------------------------
#         # Start process only if it is still PENDING.
#         #
#         # If it is already RUNNING, this means we are
#         # continuing a process after a WAITING equipment
#         # execution.
#         # -----------------------------------------------------

#         if process_execution.status == "PENDING":

#             process_execution.start_process()

#         elif process_execution.status != "RUNNING":

#             return process_execution.status

#         try:

#             equipments = list(
#                 process.equipments
#                 .filter(
#                     is_active=True,
#                 )
#                 .select_related(
#                     "equipment_type",
#                 )
#                 .order_by("id")
#                 .all()
#             )

#             if not equipments:

#                 raise ValueError(
#                     f"No equipment configured for process "
#                     f"'{process.name}'."
#                 )

#             # -------------------------------------------------
#             # Find equipment executions that have already
#             # completed for this process.
#             #
#             # This prevents a timed equipment that has already
#             # finished from being turned ON again.
#             # -------------------------------------------------

#             completed_equipment_ids = set(
#                 StageBatchProcessEquipmentExecution.objects
#                 .filter(
#                     stage_batch_process_execution=process_execution,
#                     status="COMPLETED",
#                 )
#                 .values_list(
#                     "equipment_id",
#                     flat=True,
#                 )
#             )

#             # -------------------------------------------------
#             # Execute remaining equipment one by one.
#             # -------------------------------------------------

#             for equipment in equipments:

#                 # -------------------------------------------------
#                 # If this equipment execution is already complete,
#                 # do not execute it again.
#                 # -------------------------------------------------

#                 if equipment.id in completed_equipment_ids:

#                     continue

#                 # -------------------------------------------------
#                 # Check batch status again before every equipment.
#                 # This allows STOP to prevent further operations.
#                 # -------------------------------------------------

#                 self.stage_batch.refresh_from_db(
#                     fields=["status"]
#                 )

#                 if self.stage_batch.status != "RUNNING":

#                     return self.stage_batch.status

#                 result = self.execute_equipment(
#                     process_execution,
#                     equipment,
#                 )

#                 # -------------------------------------------------
#                 # Timed equipment is now waiting.
#                 #
#                 # Do not continue to another equipment or process.
#                 # -------------------------------------------------

#                 if result == "WAITING":

#                     return "WAITING"

#             # -------------------------------------------------
#             # All equipment operations are complete.
#             # -------------------------------------------------

#             self.stage_batch.refresh_from_db(
#                 fields=["status"]
#             )

#             if self.stage_batch.status != "RUNNING":

#                 return self.stage_batch.status

#             process_execution.complete_process()

#             # -------------------------------------------------
#             # Continue to next process.
#             #
#             # This is safe because timed equipment has already
#             # returned WAITING and stopped here.
#             # -------------------------------------------------

#             return self.execute()

#         except Exception as exc:

#             # -------------------------------------------------
#             # Do not overwrite STOPPED with FAILED.
#             # -------------------------------------------------

#             self.stage_batch.refresh_from_db(
#                 fields=["status"]
#             )

#             if (
#                 self.stage_batch.status == "RUNNING"
#                 and process_execution.status == "RUNNING"
#             ):

#                 process_execution.fail_process(
#                     remarks=str(exc)
#                 )

#             raise

#     # =========================================================
#     # EXECUTE ONE EQUIPMENT
#     # =========================================================

#     def execute_equipment(
#         self,
#         process_execution,
#         equipment,
#     ):

#         # -----------------------------------------------------
#         # Validate equipment.
#         # -----------------------------------------------------

#         if not equipment.is_active:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is inactive."
#             )

#         if equipment.status in [
#             "FAULT",
#             "MAINTENANCE",
#         ]:

#             raise ValueError(
#                 f"Equipment '{equipment.name}' is "
#                 f"{equipment.status}."
#             )

#         # -----------------------------------------------------
#         # Make sure this batch is still running.
#         # -----------------------------------------------------

#         self.stage_batch.refresh_from_db(
#             fields=["status"]
#         )

#         if self.stage_batch.status != "RUNNING":

#             return self.stage_batch.status

#         # -----------------------------------------------------
#         # Create equipment execution record.
#         # -----------------------------------------------------

#         equipment_execution = (
#             StageBatchProcessEquipmentExecution.objects.create(
#                 stage_batch_process_execution=process_execution,
#                 equipment=equipment,
#                 state=None,
#             )
#         )

#         equipment_execution.start_execution()

#         try:

#             # =================================================
#             # EQUIPMENT IS OFF
#             # =================================================

#             if equipment.current_state == "OFF":

#                 # -------------------------------------------------
#                 # Turn equipment ON.
#                 # -------------------------------------------------

#                 self.turn_equipment_on(
#                     equipment,
#                 )

#                 # -------------------------------------------------
#                 # Equipment without duration completes immediately.
#                 # -------------------------------------------------

#                 if equipment.duration_seconds is None:

#                     equipment_execution.complete_execution(
#                         state="ON",
#                     )

#                     return "COMPLETED"

#                 # -------------------------------------------------
#                 # Equipment with duration.
#                 #
#                 # DO NOT WAIT HERE.
#                 #
#                 # Store the future time in scheduled_at and
#                 # change the execution to WAITING.
#                 # -------------------------------------------------

#                 scheduled_at = (
#                     timezone.now()
#                     + timedelta(
#                         seconds=equipment.duration_seconds
#                     )
#                 )

#                 equipment_execution.wait_execution(
#                     scheduled_at
#                 )

#                 print(
#                     f"{equipment.name} is ON."
#                 )

#                 print(
#                     f"Next action scheduled at: "
#                     f"{scheduled_at}"
#                 )

#                 return "WAITING"

#             # =================================================
#             # EQUIPMENT IS ALREADY ON
#             # =================================================

#             elif equipment.current_state == "ON":

#                 # -------------------------------------------------
#                 # This case is mainly useful when continuing an
#                 # existing equipment operation.
#                 # -------------------------------------------------

#                 if equipment.duration_seconds is not None:

#                     if equipment.start_time is None:

#                         raise ValueError(
#                             f"Equipment '{equipment.name}' has "
#                             f"duration configured but start_time "
#                             f"is missing."
#                         )

#                     # -------------------------------------------------
#                     # Check whether duration has completed.
#                     # -------------------------------------------------

#                     if not self.is_duration_completed(
#                         equipment
#                     ):

#                         scheduled_at = (
#                             self.get_scheduled_time(
#                                 equipment
#                             )
#                         )

#                         equipment_execution.wait_execution(
#                             scheduled_at
#                         )

#                         return "WAITING"

#                 # -------------------------------------------------
#                 # Duration completed or no duration.
#                 # Turn equipment OFF.
#                 # -------------------------------------------------

#                 self.turn_equipment_off(
#                     equipment
#                 )

#                 equipment_execution.complete_execution(
#                     state="OFF",
#                 )

#                 return "COMPLETED"

#             else:

#                 raise ValueError(
#                     f"Invalid current state "
#                     f"'{equipment.current_state}' for "
#                     f"equipment '{equipment.name}'."
#                 )

#         except Exception as exc:

#             # -----------------------------------------------------
#             # Mark equipment execution as failed.
#             # -----------------------------------------------------

#             equipment_execution.fail_execution(
#                 remarks=str(exc)
#             )

#             raise

#     # =========================================================
#     # TURN EQUIPMENT ON
#     # =========================================================

#     def turn_equipment_on(
#         self,
#         equipment,
#     ):

#         equipment.current_state = "ON"

#         # -----------------------------------------------------
#         # Timing equipment.
#         # -----------------------------------------------------

#         if equipment.duration_seconds is not None:

#             equipment.start_time = (
#                 timezone.now().time()
#             )

#             equipment.end_time = None

#             print(
#                 f"Equipment ON with timing: "
#                 f"{equipment.name} "
#                 f"({equipment.duration_seconds} seconds)"
#             )

#         else:

#             print(
#                 f"Equipment ON without timing: "
#                 f"{equipment.name}"
#             )

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "start_time",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#     # =========================================================
#     # TURN EQUIPMENT OFF
#     # =========================================================

#     def turn_equipment_off(
#         self,
#         equipment,
#     ):

#         equipment.current_state = "OFF"

#         equipment.end_time = (
#             timezone.now().time()
#         )

#         equipment.save(
#             update_fields=[
#                 "current_state",
#                 "end_time",
#                 "updated_at",
#             ]
#         )

#         print(
#             f"Equipment OFF: "
#             f"{equipment.name}"
#         )

#     # =========================================================
#     # CHECK DURATION
#     # =========================================================

#     def is_duration_completed(
#         self,
#         equipment,
#     ):

#         if equipment.duration_seconds is None:

#             return True

#         if equipment.start_time is None:

#             return False

#         scheduled_at = (
#             self.get_scheduled_time(
#                 equipment
#             )
#         )

#         return timezone.now() >= scheduled_at

#     # =========================================================
#     # GET SCHEDULED TIME
#     # =========================================================

#     def get_scheduled_time(
#         self,
#         equipment,
#     ):

#         now = timezone.now()

#         start_datetime = timezone.make_aware(
#             timezone.datetime.combine(
#                 now.date(),
#                 equipment.start_time,
#             ),
#             timezone.get_current_timezone(),
#         )

#         # -----------------------------------------------------
#         # Handle midnight crossing.
#         # -----------------------------------------------------

#         if start_datetime > now:

#             start_datetime -= timedelta(
#                 days=1
#             )

#         scheduled_at = (
#             start_datetime
#             + timedelta(
#                 seconds=equipment.duration_seconds
#             )
#         )

#         return scheduled_at

#     # =========================================================
#     # DEACTIVATE STAGE EQUIPMENT
#     # =========================================================

#     def deactivate_stage_equipment(self):

#         stage = self.stage_batch.stage

#         stage.equipments.filter(
#             is_active=True,
#         ).update(
#             current_state="OFF",
#             status="INACTIVE",
#         )






from django.utils import timezone
from datetime import timedelta

from treatment_process.models import (
    StageBatchProcessExecution,
    StageBatchProcessEquipmentExecution,
)


class StageExecutionService:
    """
    Executes a TreatmentStage without blocking the server.

    Main rules:

    1. Processes execute according to sequence.

    2. Process.equipments defines which equipment
       belongs to the process.

    3. Equipment.current_state determines the
       next operation:

           OFF -> ON
           ON  -> OFF

    4. When equipment is OFF:
           Turn it ON.
           Record the ON time.
           Complete the process operation.

    5. When equipment is ON:
           The equipment is about to be turned OFF.

           Before turning it OFF, check whether the
           configured duration has been completed.

    6. If the required duration has NOT completed:
           Create a WAITING execution.
           Store scheduled_at.
           Stop the current process temporarily.

    7. The background worker checks WAITING executions.

    8. When scheduled_at is reached:
           Turn equipment OFF.
           Complete the equipment execution.
           Continue the process.

    9. duration_seconds therefore represents the minimum
       time the equipment should remain ON.

    10. duration_seconds does NOT automatically turn
        equipment OFF after the ON process.

    11. Different stages can execute independently.

    12. STOPPED batches must never continue execution.

    13. No equipment-duration time.sleep() is used.
    """

    def __init__(self, stage_batch):
        self.stage_batch = stage_batch

    # =========================================================
    # EXECUTE STAGE
    # =========================================================

    def execute(self):

        try:

            # -------------------------------------------------
            # A stopped / completed / failed batch must never
            # continue execution.
            # -------------------------------------------------

            if self.stage_batch.status != "RUNNING":

                return self.stage_batch.status

            # -------------------------------------------------
            # Check whether there is already a RUNNING process.
            #
            # This is important when a process was waiting for
            # an equipment duration and now needs to continue.
            # -------------------------------------------------

            running_process_execution = (
                StageBatchProcessExecution.objects
                .filter(
                    stage_batch=self.stage_batch,
                    status="RUNNING",
                )
                .select_related("process")
                .first()
            )

            if running_process_execution:

                return self.execute_process(
                    running_process_execution
                )

            # -------------------------------------------------
            # Find the next PENDING process.
            # -------------------------------------------------

            process_execution = (
                StageBatchProcessExecution.objects
                .filter(
                    stage_batch=self.stage_batch,
                    status="PENDING",
                )
                .select_related("process")
                .prefetch_related("process__equipments")
                .order_by("process__sequence")
                .first()
            )

            # -------------------------------------------------
            # No PENDING process means the stage is complete.
            # -------------------------------------------------

            if not process_execution:

                self.stage_batch.complete_batch()

                self.deactivate_stage_equipment()

                return "COMPLETED"

            # -------------------------------------------------
            # Execute the process.
            # -------------------------------------------------

            return self.execute_process(
                process_execution
            )

        except Exception as exc:

            # -------------------------------------------------
            # Do not overwrite STOPPED with FAILED.
            # -------------------------------------------------

            if self.stage_batch.status == "RUNNING":

                self.stage_batch.fail_batch()

                self.deactivate_stage_equipment()

            raise exc

    # =========================================================
    # EXECUTE ONE PROCESS
    # =========================================================

    def execute_process(
        self,
        process_execution,
    ):

        # -----------------------------------------------------
        # A stopped batch must not continue.
        # -----------------------------------------------------

        if self.stage_batch.status != "RUNNING":

            return self.stage_batch.status

        process = process_execution.process

        # -----------------------------------------------------
        # Start process only if it is still PENDING.
        #
        # If already RUNNING, we are continuing a process
        # after a WAITING equipment execution.
        # -----------------------------------------------------

        if process_execution.status == "PENDING":

            process_execution.start_process()

        elif process_execution.status != "RUNNING":

            return process_execution.status

        try:

            # -------------------------------------------------
            # Get active equipment configured for this process.
            # -------------------------------------------------

            equipments = list(
                process.equipments
                .filter(
                    is_active=True,
                )
                .select_related(
                    "equipment_type",
                )
                .order_by("id")
                .all()
            )

            if not equipments:

                raise ValueError(
                    f"No equipment configured for process "
                    f"'{process.name}'."
                )

            # -------------------------------------------------
            # Find equipment executions that have already
            # completed for this process.
            #
            # This prevents completed equipment from being
            # executed again if the process is resumed.
            # -------------------------------------------------

            completed_equipment_ids = set(
                StageBatchProcessEquipmentExecution.objects
                .filter(
                    stage_batch_process_execution=process_execution,
                    status="COMPLETED",
                )
                .values_list(
                    "equipment_id",
                    flat=True,
                )
            )

            # -------------------------------------------------
            # Execute remaining equipment one by one.
            # -------------------------------------------------

            for equipment in equipments:

                if equipment.id in completed_equipment_ids:

                    continue

                # -------------------------------------------------
                # Refresh equipment from database.
                #
                # This is important because its state may have
                # changed during another worker operation.
                # -------------------------------------------------

                equipment.refresh_from_db()

                # -------------------------------------------------
                # Check batch status before every equipment.
                # -------------------------------------------------

                self.stage_batch.refresh_from_db(
                    fields=["status"]
                )

                if self.stage_batch.status != "RUNNING":

                    return self.stage_batch.status

                result = self.execute_equipment(
                    process_execution,
                    equipment,
                )

                # -------------------------------------------------
                # Equipment is waiting for its minimum ON duration.
                #
                # Do not continue to the next equipment or process.
                # -------------------------------------------------

                if result == "WAITING":

                    return "WAITING"

            # -------------------------------------------------
            # Check batch status before completing process.
            # -------------------------------------------------

            self.stage_batch.refresh_from_db(
                fields=["status"]
            )

            if self.stage_batch.status != "RUNNING":

                return self.stage_batch.status

            # -------------------------------------------------
            # All equipment operations completed.
            # -------------------------------------------------

            process_execution.complete_process()

            # -------------------------------------------------
            # Continue to next process.
            # -------------------------------------------------

            return self.execute()

        except Exception as exc:

            self.stage_batch.refresh_from_db(
                fields=["status"]
            )

            if (
                self.stage_batch.status == "RUNNING"
                and process_execution.status == "RUNNING"
            ):

                process_execution.fail_process(
                    remarks=str(exc)
                )

            raise

    # =========================================================
    # EXECUTE ONE EQUIPMENT
    # =========================================================

    def execute_equipment(
        self,
        process_execution,
        equipment,
    ):

        # -----------------------------------------------------
        # Validate equipment.
        # -----------------------------------------------------

        if not equipment.is_active:

            raise ValueError(
                f"Equipment '{equipment.name}' is inactive."
            )

        if equipment.status in [
            "FAULT",
            "MAINTENANCE",
        ]:

            raise ValueError(
                f"Equipment '{equipment.name}' is "
                f"{equipment.status}."
            )

        # -----------------------------------------------------
        # Make sure batch is still running.
        # -----------------------------------------------------

        self.stage_batch.refresh_from_db(
            fields=["status"]
        )

        if self.stage_batch.status != "RUNNING":

            return self.stage_batch.status

        # -----------------------------------------------------
        # =====================================================
        # EQUIPMENT IS OFF
        # =====================================================
        #
        # OFF -> ON
        #
        # This is the START operation.
        #
        # IMPORTANT:
        #
        # We DO NOT schedule an automatic OFF here.
        #
        # The equipment remains ON until another process
        # finds the same equipment.
        # -----------------------------------------------------

        if equipment.current_state == "OFF":

            equipment_execution = (
                StageBatchProcessEquipmentExecution.objects.create(
                    stage_batch_process_execution=process_execution,
                    equipment=equipment,
                    state=None,
                )
            )

            equipment_execution.start_execution()

            try:

                self.turn_equipment_on(
                    equipment
                )

                equipment_execution.complete_execution(
                    state="ON",
                )

                print(
                    f"Equipment ON: "
                    f"{equipment.name}"
                )

                return "COMPLETED"

            except Exception as exc:

                equipment_execution.fail_execution(
                    remarks=str(exc)
                )

                raise

        # =====================================================
        # EQUIPMENT IS ON
        # =====================================================
        #
        # ON -> OFF
        #
        # Before turning OFF, check whether the configured
        # duration has elapsed.
        #
        # If not elapsed:
        #
        #     WAITING
        #
        # Worker will come back later.
        # =====================================================

        elif equipment.current_state == "ON":

            # -------------------------------------------------
            # If duration is configured, determine whether
            # the minimum ON duration has completed.
            # -------------------------------------------------

            if equipment.duration_seconds is not None:

                if equipment.start_time is None:

                    raise ValueError(
                        f"Equipment '{equipment.name}' has "
                        f"duration configured but start_time "
                        f"is missing."
                    )

                scheduled_at = (
                    self.get_scheduled_time(
                        equipment
                    )
                )

                # -------------------------------------------------
                # Required duration has NOT completed.
                # -------------------------------------------------

                if timezone.now() < scheduled_at:

                    equipment_execution = (
                        StageBatchProcessEquipmentExecution.objects.create(
                            stage_batch_process_execution=process_execution,
                            equipment=equipment,
                            state="ON",
                        )
                    )

                    equipment_execution.start_execution()

                    equipment_execution.wait_execution(
                        scheduled_at
                    )

                    print(
                        f"Equipment '{equipment.name}' "
                        f"is still ON."
                    )

                    print(
                        f"Waiting until: "
                        f"{scheduled_at}"
                    )

                    return "WAITING"

            # -------------------------------------------------
            # Required duration has completed.
            #
            # OR equipment has no duration configured.
            #
            # Now perform:
            #
            # ON -> OFF
            # -------------------------------------------------

            equipment_execution = (
                StageBatchProcessEquipmentExecution.objects.create(
                    stage_batch_process_execution=process_execution,
                    equipment=equipment,
                    state="ON",
                )
            )

            equipment_execution.start_execution()

            try:

                self.turn_equipment_off(
                    equipment
                )

                equipment_execution.complete_execution(
                    state="OFF",
                )

                print(
                    f"Equipment OFF: "
                    f"{equipment.name}"
                )

                return "COMPLETED"

            except Exception as exc:

                equipment_execution.fail_execution(
                    remarks=str(exc)
                )

                raise

        # =====================================================
        # INVALID STATE
        # =====================================================

        else:

            raise ValueError(
                f"Invalid current state "
                f"'{equipment.current_state}' for "
                f"equipment '{equipment.name}'."
            )

    # =========================================================
    # TURN EQUIPMENT ON
    # =========================================================

    def turn_equipment_on(
        self,
        equipment,
    ):

        # -----------------------------------------------------
        # Change equipment state.
        # -----------------------------------------------------

        equipment.current_state = "ON"

        # -----------------------------------------------------
        # Record ON time.
        #
        # This is the beginning of the actual running period.
        # -----------------------------------------------------

        equipment.start_time = timezone.now().time()

        # -----------------------------------------------------
        # There is no OFF time yet.
        # -----------------------------------------------------

        equipment.end_time = None

        equipment.save(
            update_fields=[
                "current_state",
                "start_time",
                "end_time",
                "updated_at",
            ]
        )

    # =========================================================
    # TURN EQUIPMENT OFF
    # =========================================================

    def turn_equipment_off(
        self,
        equipment,
    ):

        # -----------------------------------------------------
        # Change equipment state.
        # -----------------------------------------------------

        equipment.current_state = "OFF"

        # -----------------------------------------------------
        # Record OFF time.
        # -----------------------------------------------------

        equipment.end_time = timezone.now().time()

        equipment.save(
            update_fields=[
                "current_state",
                "end_time",
                "updated_at",
            ]
        )

    # =========================================================
    # GET SCHEDULED OFF TIME
    # =========================================================

    def get_scheduled_time(
        self,
        equipment,
    ):

        # -----------------------------------------------------
        # Current timezone-aware datetime.
        # -----------------------------------------------------

        now = timezone.now()

        # -----------------------------------------------------
        # Equipment.start_time is currently a TimeField.
        #
        # Convert it into today's datetime.
        # -----------------------------------------------------

        start_datetime = timezone.make_aware(
            timezone.datetime.combine(
                now.date(),
                equipment.start_time,
            ),
            timezone.get_current_timezone(),
        )

        # -----------------------------------------------------
        # Handle midnight crossing.
        #
        # If today's start time is in the future relative
        # to now, the equipment was started yesterday.
        # -----------------------------------------------------

        if start_datetime > now:

            start_datetime -= timedelta(
                days=1
            )

        # -----------------------------------------------------
        # Add configured duration.
        #
        # This represents the earliest time at which the
        # equipment can be turned OFF.
        # -----------------------------------------------------

        scheduled_at = (
            start_datetime
            + timedelta(
                seconds=equipment.duration_seconds
            )
        )

        return scheduled_at

    # =========================================================
    # DEACTIVATE STAGE EQUIPMENT
    # =========================================================

    def deactivate_stage_equipment(self):

        stage = self.stage_batch.stage

        # -----------------------------------------------------
        # When the complete stage finishes:
        #
        # 1. Equipment becomes OFF.
        # 2. Equipment becomes INACTIVE.
        # -----------------------------------------------------

        stage.equipments.filter(
            is_active=True,
        ).update(
            current_state="OFF",
            status="INACTIVE",
        )