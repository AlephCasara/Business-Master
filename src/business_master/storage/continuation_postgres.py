from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.capital import CapitalRequirement
from business_master.domain.clock import utcnow
from business_master.domain.decisions import (
    AutonomousContinuationRequest,
    AutonomousContinuationResult,
    AutonomousDecision,
    ContinuationKind,
)
from business_master.domain.enums import ExperimentStatus
from business_master.domain.experiment_contracts import ExperimentContract
from business_master.domain.experiments import Experiment
from business_master.domain.family_evaluation import FamilyEvaluation
from business_master.domain.portfolio import (
    PortfolioAllocation,
    PortfolioValueEstimate,
    RiskAssessment,
)
from business_master.domain.resources import ResourceReservation, ResourceVector
from business_master.policies.continuation import ContinuationPolicy
from business_master.storage.resource_reservations_postgres import (
    ReservationExpiryError,
    ResourceCapacityError,
    ResourceNotFoundError,
    ResourceUnavailableError,
)


class ContinuationError(RuntimeError):
    """Base error for durable PR10 continuation failures."""


class ContinuationConflictError(ContinuationError):
    """Raised when idempotency/allocation authority was already consumed differently."""


class ContinuationNotFoundError(ContinuationError):
    """Raised when required persisted lineage is missing."""


class StaleContinuationError(ContinuationError):
    """Raised when newer belief/evaluation state invalidates an allocation."""


class ContinuationLineageError(ContinuationError):
    """Raised when persisted parent/allocation/contract lineage disagrees."""


class ContinuationStateError(ContinuationError):
    """Raised when operational state cannot legitimately produce a child."""


class PostgresContinuationStore:
    """Serializable Decision → reservation → child-experiment materialization."""

    def __init__(
        self,
        dsn: str,
        *,
        clock: Callable[[], datetime] = utcnow,
    ) -> None:
        self._dsn = dsn
        self._clock = clock

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("continuation store clock must return a timezone-aware timestamp")
        return value

    def continue_from(
        self,
        request: AutonomousContinuationRequest,
        *,
        policy: ContinuationPolicy | None = None,
    ) -> AutonomousContinuationResult:
        effective_policy = policy or ContinuationPolicy()
        decided_at = self._now()

        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            conn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"continuation:{request.idempotency_key}",),
            )

            existing = self._load_decision_by_key(conn, request.idempotency_key)
            if existing is not None:
                self._assert_same_request(existing, request)
                return self._load_result(conn, existing)

            allocation_row = conn.execute(
                """
                SELECT pa.*
                FROM portfolio_allocation AS pa
                WHERE pa.id = %s
                FOR UPDATE
                """,
                (request.portfolio_allocation_id,),
            ).fetchone()
            if allocation_row is None:
                raise ContinuationNotFoundError("portfolio allocation does not exist")
            allocation = self._allocation_from_row(allocation_row)

            prior = conn.execute(
                """
                SELECT id, idempotency_key
                FROM decision
                WHERE portfolio_allocation_id = %s
                LIMIT 1
                """,
                (allocation.id,),
            ).fetchone()
            if prior is not None:
                raise ContinuationConflictError(
                    "portfolio allocation already produced an autonomous decision; "
                    "replan is required"
                )

            evaluation_row = conn.execute(
                "SELECT * FROM family_evaluation WHERE id = %s",
                (allocation.family_evaluation_id,),
            ).fetchone()
            if evaluation_row is None:
                raise ContinuationNotFoundError("family evaluation does not exist")
            evaluation = self._evaluation_from_row(evaluation_row)

            self._assert_fresh_lineage(conn, allocation, evaluation)

            parent_row = conn.execute(
                """
                SELECT e.*, binding.contract_id AS bound_contract_id
                FROM experiment AS e
                LEFT JOIN experiment_contract_binding AS binding
                  ON binding.experiment_id = e.id
                WHERE e.id = %s
                FOR UPDATE OF e
                """,
                (request.parent_experiment_id,),
            ).fetchone()
            if parent_row is None:
                raise ContinuationNotFoundError("parent experiment does not exist")
            self._validate_parent(parent_row, allocation)

            source_contract_row = conn.execute(
                "SELECT * FROM experiment_contract WHERE id = %s",
                (allocation.contract_id,),
            ).fetchone()
            if source_contract_row is None:
                raise ContinuationNotFoundError("source experiment contract does not exist")
            source_contract = self._contract_from_row(source_contract_row)
            if source_contract.economic_hypothesis_id != allocation.hypothesis_id:
                raise ContinuationLineageError(
                    "source contract belongs to a different economic hypothesis"
                )
            if source_contract.business_family != str(parent_row["business_family"]):
                raise ContinuationLineageError(
                    "parent experiment business family differs from source contract"
                )

            self._expire_due_capital(conn, allocation.id, decided_at)
            capital_authorization_id = self._active_capital_authorization_id(
                conn,
                allocation.id,
            )

            decision = effective_policy.decide(
                request,
                allocation,
                evaluation,
                decided_at=decided_at,
                capital_authorization_id=capital_authorization_id,
            ).model_copy(update={"reservation_expires_at": request.reservation_expires_at})

            creates_child = decision.continuation_kind is not ContinuationKind.NONE
            if creates_child and parent_row["status"] not in {"measuring", "complete"}:
                raise ContinuationStateError(
                    "child continuation requires a measuring or complete parent experiment"
                )

            self._insert_decision(conn, decision, allocation)
            if not creates_child:
                return AutonomousContinuationResult(decision=decision)

            assert decision.child_contract_id is not None
            assert decision.child_experiment_id is not None
            assert decision.target_tier is not None

            child_contract = self._build_child_contract(
                decision,
                source_contract,
            )
            self._insert_contract(conn, child_contract)

            reservation = self._reserve_resources(
                conn,
                decision,
                decided_at=decided_at,
            )

            child_experiment = Experiment(
                id=decision.child_experiment_id,
                hypothesis_id=parent_row["hypothesis_id"],
                parent_id=request.parent_experiment_id,
                status=ExperimentStatus.PLANNED,
                tier=decision.target_tier,
                business_family=source_contract.business_family,
                channel_id=parent_row["channel_id"],
                product_id=parent_row["product_id"],
                mutation=None,
                dimensions=parent_row["dimensions"],
                expected_cash_cost=child_contract.budget.max_cash_cost,
                expected_compute_units=child_contract.budget.max_compute_units,
                expected_human_minutes=child_contract.budget.max_human_minutes,
                created_at=decided_at,
            )
            self._insert_experiment(conn, child_experiment)
            conn.execute(
                """
                INSERT INTO experiment_contract_binding (experiment_id, contract_id, bound_at)
                VALUES (%s, %s, %s)
                """,
                (child_experiment.id, child_contract.id, decided_at),
            )

            reservation_id = None if reservation is None else reservation.id
            conn.execute(
                """
                UPDATE decision
                SET child_experiment_id = %s,
                    child_contract_id = %s,
                    resource_reservation_id = %s
                WHERE id = %s
                """,
                (
                    child_experiment.id,
                    child_contract.id,
                    reservation_id,
                    decision.id,
                ),
            )
            decision = decision.model_copy(
                update={"resource_reservation_id": reservation_id}
            )
            return AutonomousContinuationResult(
                decision=decision,
                child_experiment=child_experiment,
                child_contract=child_contract,
                resource_reservation=reservation,
            )

    def get_by_idempotency_key(self, key: str) -> AutonomousContinuationResult | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            decision = self._load_decision_by_key(conn, key)
            if decision is None:
                return None
            return self._load_result(conn, decision)

    @staticmethod
    def _assert_same_request(
        decision: AutonomousDecision,
        request: AutonomousContinuationRequest,
    ) -> None:
        if (
            decision.parent_experiment_id != request.parent_experiment_id
            or decision.portfolio_allocation_id != request.portfolio_allocation_id
            or decision.reservation_expires_at != request.reservation_expires_at
        ):
            raise ContinuationConflictError(
                "continuation idempotency key was reused with different semantics"
            )

    @staticmethod
    def _assert_fresh_lineage(
        conn: psycopg.Connection[dict[str, Any]],
        allocation: PortfolioAllocation,
        evaluation: FamilyEvaluation,
    ) -> None:
        latest_evaluation = conn.execute(
            """
            SELECT id
            FROM family_evaluation
            WHERE hypothesis_id = %s
            ORDER BY evaluated_at DESC, created_at DESC, id DESC
            LIMIT 1
            """,
            (allocation.hypothesis_id,),
        ).fetchone()
        if latest_evaluation is None or latest_evaluation["id"] != evaluation.id:
            raise StaleContinuationError(
                "portfolio allocation no longer references the latest family evaluation"
            )

        latest_belief = conn.execute(
            """
            SELECT state_version
            FROM belief_state_version
            WHERE hypothesis_id = %s
            ORDER BY state_version DESC
            LIMIT 1
            """,
            (allocation.hypothesis_id,),
        ).fetchone()
        if latest_belief is None:
            raise ContinuationNotFoundError("no persisted belief-state version exists")
        if int(latest_belief["state_version"]) != allocation.belief_state_version:
            raise StaleContinuationError(
                "portfolio allocation no longer references the latest belief-state version"
            )

    @staticmethod
    def _validate_parent(row: dict[str, Any], allocation: PortfolioAllocation) -> None:
        if row["bound_contract_id"] is None:
            raise ContinuationLineageError("parent experiment has no V2 contract binding")
        if row["bound_contract_id"] != allocation.contract_id:
            raise ContinuationLineageError(
                "parent experiment is bound to a different source contract"
            )
        if str(row["tier"]) != allocation.current_tier.value:
            raise ContinuationLineageError(
                "parent experiment tier differs from portfolio allocation tier"
            )

    @staticmethod
    def _expire_due_capital(
        conn: psycopg.Connection[dict[str, Any]],
        allocation_id: UUID,
        as_of: datetime,
    ) -> None:
        conn.execute(
            """
            UPDATE capital_authorization
            SET status = 'expired', released_at = %s, expired_at = %s
            WHERE portfolio_allocation_id = %s
              AND status = 'active'
              AND expires_at IS NOT NULL
              AND expires_at <= %s
            """,
            (as_of, as_of, allocation_id, as_of),
        )

    @staticmethod
    def _active_capital_authorization_id(
        conn: psycopg.Connection[dict[str, Any]],
        allocation_id: UUID,
    ) -> UUID | None:
        row = conn.execute(
            """
            SELECT id
            FROM capital_authorization
            WHERE portfolio_allocation_id = %s AND status = 'active'
            LIMIT 1
            """,
            (allocation_id,),
        ).fetchone()
        return None if row is None else row["id"]

    @staticmethod
    def _insert_decision(
        conn: psycopg.Connection[dict[str, Any]],
        decision: AutonomousDecision,
        allocation: PortfolioAllocation,
    ) -> None:
        payload = decision.model_dump(mode="json")
        chosen_action = {
            "continuation_kind": decision.continuation_kind.value,
            "target_tier": None if decision.target_tier is None else decision.target_tier.value,
            "child_experiment_id": (
                None if decision.child_experiment_id is None else str(decision.child_experiment_id)
            ),
            "child_contract_id": (
                None if decision.child_contract_id is None else str(decision.child_contract_id)
            ),
        }
        expected_cash = (
            Decimal(0)
            if allocation.capital_requirement is None
            else allocation.capital_requirement.amount
        )
        conn.execute(
            """
            INSERT INTO decision (
                id, entity_id, decision_type, policy_name, policy_version,
                evidence_ids, observed_features, chosen_action, expected_value,
                expected_cash_cost, expected_compute_units, expected_human_minutes,
                risk, rationale, created_at,
                idempotency_key, parent_experiment_id, portfolio_allocation_id,
                family_evaluation_id, hypothesis_id, source_contract_id,
                belief_state_version, continuation_kind, target_tier,
                expected_resource_demand, capital_requirement, blast_radius,
                reversible, human_gate_required, reservation_expires_at,
                child_experiment_id, child_contract_id, resource_reservation_id,
                capital_authorization_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                NULL, NULL, NULL, %s
            )
            """,
            (
                decision.id,
                decision.parent_experiment_id,
                decision.decision_type.value,
                decision.policy_name,
                decision.policy_version,
                decision.evidence_ids,
                Jsonb(payload["observed_features"]),
                Jsonb(chosen_action),
                allocation.value.economic_value,
                expected_cash,
                0.0,
                0.0,
                decision.risk.level.value,
                decision.rationale,
                decision.created_at,
                decision.idempotency_key,
                decision.parent_experiment_id,
                decision.portfolio_allocation_id,
                decision.family_evaluation_id,
                decision.hypothesis_id,
                decision.source_contract_id,
                decision.belief_state_version,
                decision.continuation_kind.value,
                None if decision.target_tier is None else decision.target_tier.value,
                Jsonb(payload["expected_resource_demand"]),
                (
                    None
                    if decision.capital_requirement is None
                    else Jsonb(payload["capital_requirement"])
                ),
                decision.risk.blast_radius,
                decision.risk.reversible,
                decision.risk.human_gate_required,
                decision.reservation_expires_at,
                decision.capital_authorization_id,
            ),
        )

    @staticmethod
    def _build_child_contract(
        decision: AutonomousDecision,
        source: ExperimentContract,
    ) -> ExperimentContract:
        assert decision.child_contract_id is not None
        return ExperimentContract(
            id=decision.child_contract_id,
            economic_hypothesis_id=source.economic_hypothesis_id,
            business_family=source.business_family,
            question=source.question,
            intervention_dimensions=source.intervention_dimensions,
            held_constant_dimensions=source.held_constant_dimensions,
            expected_observation=source.expected_observation,
            falsification_condition=source.falsification_condition,
            measurement=source.measurement,
            resource_requirements=source.resource_requirements,
            budget=source.budget,
            parent_contract_id=source.id,
            supersedes_contract_id=(
                source.id
                if decision.continuation_kind is ContinuationKind.GRADUATE
                else None
            ),
            origin_decision_id=decision.id,
            contract_version=source.contract_version + 1,
            created_at=decision.created_at,
        )

    @staticmethod
    def _insert_contract(
        conn: psycopg.Connection[dict[str, Any]],
        contract: ExperimentContract,
    ) -> None:
        payload = contract.model_dump(mode="json")
        conn.execute(
            """
            INSERT INTO experiment_contract (
                id, economic_hypothesis_id, business_family, question,
                intervention_dimensions, held_constant_dimensions,
                expected_observation, falsification_condition, measurement,
                resource_requirements, budget, parent_contract_id,
                supersedes_contract_id, origin_decision_id, contract_version, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                contract.id,
                contract.economic_hypothesis_id,
                contract.business_family,
                contract.question,
                Jsonb(payload["intervention_dimensions"]),
                contract.held_constant_dimensions,
                contract.expected_observation,
                contract.falsification_condition,
                Jsonb(payload["measurement"]),
                Jsonb(payload["resource_requirements"]["quantities"]),
                Jsonb(payload["budget"]),
                contract.parent_contract_id,
                contract.supersedes_contract_id,
                contract.origin_decision_id,
                contract.contract_version,
                contract.created_at,
            ),
        )

    @staticmethod
    def _insert_experiment(
        conn: psycopg.Connection[dict[str, Any]],
        experiment: Experiment,
    ) -> None:
        conn.execute(
            """
            INSERT INTO experiment (
                id, hypothesis_id, parent_id, status, tier, business_family,
                channel_id, product_id, mutation, dimensions,
                expected_cash_cost, expected_compute_units, expected_human_minutes,
                created_at, started_at, completed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                experiment.id,
                experiment.hypothesis_id,
                experiment.parent_id,
                experiment.status.value,
                experiment.tier.value,
                experiment.business_family,
                experiment.channel_id,
                experiment.product_id,
                None,
                Jsonb(experiment.dimensions),
                experiment.expected_cash_cost,
                experiment.expected_compute_units,
                experiment.expected_human_minutes,
                experiment.created_at,
                experiment.started_at,
                experiment.completed_at,
            ),
        )

    @staticmethod
    def _reserve_resources(
        conn: psycopg.Connection[dict[str, Any]],
        decision: AutonomousDecision,
        *,
        decided_at: datetime,
    ) -> ResourceReservation | None:
        requirements = decision.expected_resource_demand
        if not requirements.quantities:
            return None
        if (
            decision.reservation_expires_at is not None
            and decision.reservation_expires_at <= decided_at
        ):
            raise ReservationExpiryError("reservation expires_at must be in the future")

        conn.execute(
            """
            UPDATE resource_reservation
            SET status = 'released', released_at = %s, expired_at = %s
            WHERE status = 'active'
              AND expires_at IS NOT NULL
              AND expires_at <= %s
            """,
            (decided_at, decided_at, decided_at),
        )

        names = sorted(requirements.quantities)
        resource_rows = conn.execute(
            """
            SELECT id, name, available, capacity
            FROM resource
            WHERE name = ANY(%s)
            ORDER BY name
            FOR UPDATE
            """,
            (names,),
        ).fetchall()
        rows_by_name = {str(row["name"]): row for row in resource_rows}
        missing = sorted(set(names) - set(rows_by_name))
        if missing:
            raise ResourceNotFoundError(missing)
        unavailable = sorted(
            name for name, row in rows_by_name.items() if not bool(row["available"])
        )
        if unavailable:
            raise ResourceUnavailableError(unavailable)

        resource_ids = [row["id"] for row in resource_rows]
        reserved_rows = conn.execute(
            """
            SELECT item.resource_id, COALESCE(SUM(item.amount), 0) AS reserved
            FROM resource_reservation_item AS item
            JOIN resource_reservation AS reservation
              ON reservation.id = item.reservation_id
            WHERE item.resource_id = ANY(%s)
              AND reservation.status = 'active'
            GROUP BY item.resource_id
            """,
            (resource_ids,),
        ).fetchall()
        reserved_by_id = {
            row["resource_id"]: Decimal(row["reserved"]) for row in reserved_rows
        }
        for name in names:
            row = rows_by_name[name]
            capacity = Decimal(str(row["capacity"]))
            reserved = reserved_by_id.get(row["id"], Decimal(0))
            available = max(capacity - reserved, Decimal(0))
            requested = requirements.amount(name)
            if requested > available:
                raise ResourceCapacityError(
                    name,
                    requested=requested,
                    available=available,
                )

        assert decision.child_experiment_id is not None
        reservation = ResourceReservation(
            id=AutonomousDecision.deterministic_reservation_id(decision.id),
            owner_type="experiment",
            owner_id=decision.child_experiment_id,
            idempotency_key=f"pr10:{decision.id}:resources",
            requirements=requirements,
            created_at=decided_at,
            expires_at=decision.reservation_expires_at,
        )
        conn.execute(
            """
            INSERT INTO resource_reservation (
                id, owner_type, owner_id, idempotency_key, requirements,
                status, created_at, expires_at, released_at, expired_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                reservation.id,
                reservation.owner_type,
                reservation.owner_id,
                reservation.idempotency_key,
                Jsonb(reservation.requirements.model_dump(mode="json")["quantities"]),
                reservation.status.value,
                reservation.created_at,
                reservation.expires_at,
                reservation.released_at,
                reservation.expired_at,
            ),
        )
        for name, amount in requirements.quantities.items():
            conn.execute(
                """
                INSERT INTO resource_reservation_item (reservation_id, resource_id, amount)
                VALUES (%s, %s, %s)
                """,
                (reservation.id, rows_by_name[name]["id"], amount),
            )
        return reservation

    def _load_decision_by_key(
        self,
        conn: psycopg.Connection[dict[str, Any]],
        key: str,
    ) -> AutonomousDecision | None:
        row = conn.execute(
            "SELECT * FROM decision WHERE idempotency_key = %s",
            (key,),
        ).fetchone()
        return None if row is None else self._decision_from_row(row)

    def _load_result(
        self,
        conn: psycopg.Connection[dict[str, Any]],
        decision: AutonomousDecision,
    ) -> AutonomousContinuationResult:
        child = None
        contract = None
        reservation = None
        if decision.child_experiment_id is not None:
            row = conn.execute(
                "SELECT * FROM experiment WHERE id = %s",
                (decision.child_experiment_id,),
            ).fetchone()
            if row is None:
                raise ContinuationLineageError("persisted decision child experiment is missing")
            child = self._experiment_from_row(row)
        if decision.child_contract_id is not None:
            row = conn.execute(
                "SELECT * FROM experiment_contract WHERE id = %s",
                (decision.child_contract_id,),
            ).fetchone()
            if row is None:
                raise ContinuationLineageError("persisted decision child contract is missing")
            contract = self._contract_from_row(row)
        if decision.resource_reservation_id is not None:
            row = conn.execute(
                "SELECT * FROM resource_reservation WHERE id = %s",
                (decision.resource_reservation_id,),
            ).fetchone()
            if row is None:
                raise ContinuationLineageError("persisted decision resource reservation is missing")
            reservation = self._reservation_from_row(row)
        return AutonomousContinuationResult(
            decision=decision,
            child_experiment=child,
            child_contract=contract,
            resource_reservation=reservation,
        )

    @staticmethod
    def _allocation_from_row(row: dict[str, Any]) -> PortfolioAllocation:
        capital = None
        if row["capital_amount"] is not None:
            capital = CapitalRequirement(
                amount=row["capital_amount"],
                currency=row["capital_currency"],
                category=row["capital_category"],
            )
        return PortfolioAllocation(
            id=row["id"],
            candidate_id=row["candidate_id"],
            family_evaluation_id=row["family_evaluation_id"],
            hypothesis_id=row["hypothesis_id"],
            contract_id=row["contract_id"],
            belief_state_version=row["belief_state_version"],
            current_tier=row["current_tier"],
            recommendation=row["recommendation"],
            roles=tuple(row["roles"]),
            group_key=row["group_key"],
            resource_demand=ResourceVector.model_validate(row["resource_demand"]),
            value=PortfolioValueEstimate.model_validate(row["value_estimate"]),
            risk=RiskAssessment.model_validate(row["risk_assessment"]),
            capital_requirement=capital,
            utility=row["utility"],
            scarcity_pressure=row["scarcity_pressure"],
            rationale=row["rationale"],
        )

    @staticmethod
    def _evaluation_from_row(row: dict[str, Any]) -> FamilyEvaluation:
        return FamilyEvaluation(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            family=row["family"],
            hypothesis_id=row["hypothesis_id"],
            contract_id=row["contract_id"],
            belief_state_version=row["belief_state_version"],
            current_tier=row["current_tier"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            evidence_ids=row["evidence_ids"],
            interpretations=row["interpretations"],
            criteria=row["criteria"],
            external_observations=row["external_observations"],
            independent_sources=row["independent_sources"],
            replication_count=row["replication_count"],
            distinct_contexts=row["distinct_contexts"],
            evidence_sufficient=row["evidence_sufficient"],
            supporting_signal=row["supporting_signal"],
            falsified=row["falsified"],
            economic_readiness=row["economic_readiness"],
            operational_readiness=row["operational_readiness"],
            recommendation=row["recommendation"],
            rationale=row["rationale"],
            evaluated_at=row["evaluated_at"],
        )

    @staticmethod
    def _contract_from_row(row: dict[str, Any]) -> ExperimentContract:
        return ExperimentContract(
            id=row["id"],
            economic_hypothesis_id=row["economic_hypothesis_id"],
            business_family=row["business_family"],
            question=row["question"],
            intervention_dimensions=row["intervention_dimensions"],
            held_constant_dimensions=row["held_constant_dimensions"],
            expected_observation=row["expected_observation"],
            falsification_condition=row["falsification_condition"],
            measurement=row["measurement"],
            resource_requirements=ResourceVector(quantities=row["resource_requirements"]),
            budget=row["budget"],
            parent_contract_id=row["parent_contract_id"],
            supersedes_contract_id=row["supersedes_contract_id"],
            origin_decision_id=row["origin_decision_id"],
            contract_version=row["contract_version"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _experiment_from_row(row: dict[str, Any]) -> Experiment:
        return Experiment(
            id=row["id"],
            hypothesis_id=row["hypothesis_id"],
            parent_id=row["parent_id"],
            status=row["status"],
            tier=row["tier"],
            business_family=row["business_family"],
            channel_id=row["channel_id"],
            product_id=row["product_id"],
            mutation=row["mutation"],
            dimensions=row["dimensions"],
            expected_cash_cost=float(row["expected_cash_cost"]),
            expected_compute_units=row["expected_compute_units"],
            expected_human_minutes=row["expected_human_minutes"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )

    @staticmethod
    def _reservation_from_row(row: dict[str, Any]) -> ResourceReservation:
        return ResourceReservation(
            id=row["id"],
            owner_type=row["owner_type"],
            owner_id=row["owner_id"],
            idempotency_key=row["idempotency_key"],
            requirements=ResourceVector(quantities=row["requirements"]),
            status=row["status"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            released_at=row["released_at"],
            expired_at=row["expired_at"],
        )

    @staticmethod
    def _decision_from_row(row: dict[str, Any]) -> AutonomousDecision:
        capital = None
        if row["capital_requirement"] is not None:
            capital = CapitalRequirement.model_validate(row["capital_requirement"])
        return AutonomousDecision(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            parent_experiment_id=row["parent_experiment_id"],
            portfolio_allocation_id=row["portfolio_allocation_id"],
            family_evaluation_id=row["family_evaluation_id"],
            hypothesis_id=row["hypothesis_id"],
            source_contract_id=row["source_contract_id"],
            belief_state_version=row["belief_state_version"],
            decision_type=row["decision_type"],
            continuation_kind=row["continuation_kind"],
            target_tier=row["target_tier"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            evidence_ids=row["evidence_ids"],
            observed_features=row["observed_features"],
            expected_resource_demand=ResourceVector.model_validate(
                row["expected_resource_demand"]
            ),
            capital_requirement=capital,
            risk=RiskAssessment(
                level=row["risk"],
                blast_radius=row["blast_radius"],
                reversible=row["reversible"],
                human_gate_required=row["human_gate_required"],
            ),
            rationale=row["rationale"],
            reservation_expires_at=row["reservation_expires_at"],
            child_experiment_id=row["child_experiment_id"],
            child_contract_id=row["child_contract_id"],
            resource_reservation_id=row["resource_reservation_id"],
            capital_authorization_id=row["capital_authorization_id"],
            created_at=row["created_at"],
        )
