from django.db import close_old_connections

from treatment_process.models import StageBatch

from treatment_process.services.stage_controller import (
    StageExecutionService,
)


def run_stage_batch(stage_batch_id):
    """
    Execute a StageBatch in the background.
    """

    try:

        # -----------------------------------------------------
        # Close any old database connection.
        # -----------------------------------------------------

        close_old_connections()

        # -----------------------------------------------------
        # Get a fresh StageBatch object.
        # -----------------------------------------------------

        stage_batch = (
            StageBatch.objects
            .select_related("stage")
            .get(
                id=stage_batch_id,
            )
        )

        # -----------------------------------------------------
        # Execute stage.
        # -----------------------------------------------------

        service = StageExecutionService(
            stage_batch=stage_batch,
        )

        service.execute()

    except StageBatch.DoesNotExist:

        print(
            f"StageBatch with ID {stage_batch_id} "
            f"does not exist."
        )

    except Exception as exc:

        print(
            f"StageBatch {stage_batch_id} "
            f"background execution failed: {exc}"
        )

    finally:

        # -----------------------------------------------------
        # Close background thread database connection.
        # -----------------------------------------------------

        close_old_connections()