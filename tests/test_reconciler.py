from uuid import uuid4

from business_master.controllers.reconciler import (
    ReconcileActionType,
    ReconcilePolicy,
    ReconcileSnapshot,
)


def test_feedback_work_outranks_new_production() -> None:
    due = uuid4()
    ready = uuid4()
    runnable = uuid4()
    probe = uuid4()

    actions = ReconcilePolicy().plan(
        ReconcileSnapshot(
            hypotheses_without_live_experiment=(probe,),
            runnable_experiments=(runnable,),
            experiments_due_for_measurement=(due,),
            experiments_ready_for_evaluation=(ready,),
            available_execution_slots=1,
            available_probe_slots=1,
        )
    )

    assert [action.kind for action in actions[:2]] == [
        ReconcileActionType.REQUEST_MEASUREMENT,
        ReconcileActionType.EVALUATE_EXPERIMENT,
    ]


def test_reconciler_does_not_overfill_execution_capacity() -> None:
    runnable = tuple(uuid4() for _ in range(5))
    actions = ReconcilePolicy().plan(
        ReconcileSnapshot(
            runnable_experiments=runnable,
            available_execution_slots=2,
        )
    )

    dispatched = [a for a in actions if a.kind == ReconcileActionType.DISPATCH_EXPERIMENT]
    assert len(dispatched) == 2


def test_hypothesis_spawns_probe_without_human_prompt() -> None:
    hypothesis_id = uuid4()
    actions = ReconcilePolicy().plan(
        ReconcileSnapshot(
            hypotheses_without_live_experiment=(hypothesis_id,),
            available_probe_slots=1,
        )
    )

    assert len(actions) == 1
    assert actions[0].kind == ReconcileActionType.CREATE_PROBE
    assert actions[0].entity_id == hypothesis_id
