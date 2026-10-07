from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.capital import CapitalRequirement
from business_master.domain.portfolio import (
    PortfolioAllocation,
    PortfolioCandidateEvaluation,
    PortfolioPlan,
    PortfolioValueEstimate,
    RiskAssessment,
)
from business_master.domain.resources import ResourceVector


class PortfolioPlanConflictError(RuntimeError):
    """Raised when an idempotency key is reused with different portfolio semantics."""


class PostgresPortfolioStore:
    """Append-only persistence for deterministic portfolio plans."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save(self, plan: PortfolioPlan) -> PortfolioPlan:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (plan.idempotency_key,),
            )
            existing = self._load_by_idempotency(conn, plan.idempotency_key)
            if existing is not None:
                if existing != plan:
                    raise PortfolioPlanConflictError(
                        "portfolio idempotency key was reused with different semantics"
                    )
                return existing

            self._validate_lineage(conn, plan)
            payload = plan.model_dump(mode="json")
            conn.execute(
                """
                INSERT INTO portfolio_plan (
                    id, idempotency_key, policy_name, policy_version,
                    policy_parameters, available_resources, evaluations, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    plan.id,
                    plan.idempotency_key,
                    plan.policy_name,
                    plan.policy_version,
                    Jsonb(payload["policy_parameters"]),
                    Jsonb(payload["available_resources"]),
                    Jsonb(payload["evaluations"]),
                    plan.created_at,
                ),
            )
            for allocation in plan.allocations:
                capital = allocation.capital_requirement
                conn.execute(
                    """
                    INSERT INTO portfolio_allocation (
                        id, plan_id, candidate_id, family_evaluation_id, hypothesis_id,
                        contract_id, belief_state_version, current_tier, recommendation,
                        roles, group_key, resource_demand, value_estimate, risk_assessment,
                        capital_amount, capital_currency, capital_category, utility,
                        scarcity_pressure, rationale
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        allocation.id,
                        plan.id,
                        allocation.candidate_id,
                        allocation.family_evaluation_id,
                        allocation.hypothesis_id,
                        allocation.contract_id,
                        allocation.belief_state_version,
                        allocation.current_tier.value,
                        allocation.recommendation.value,
                        Jsonb([role.value for role in allocation.roles]),
                        allocation.group_key,
                        Jsonb(allocation.resource_demand.model_dump(mode="json")),
                        Jsonb(allocation.value.model_dump(mode="json")),
                        Jsonb(allocation.risk.model_dump(mode="json")),
                        None if capital is None else capital.amount,
                        None if capital is None else capital.currency,
                        None if capital is None else capital.category.value,
                        allocation.utility,
                        allocation.scarcity_pressure,
                        allocation.rationale,
                    ),
                )
            return plan

    @staticmethod
    def _validate_lineage(conn: Any, plan: PortfolioPlan) -> None:
        for allocation in plan.allocations:
            evaluation = conn.execute(
                """
                SELECT hypothesis_id, contract_id, belief_state_version,
                       current_tier, recommendation
                FROM family_evaluation
                WHERE id = %s
                """,
                (allocation.family_evaluation_id,),
            ).fetchone()
            if evaluation is None:
                raise ValueError("portfolio allocation family evaluation does not exist")
            if evaluation["hypothesis_id"] != allocation.hypothesis_id:
                raise ValueError("portfolio allocation hypothesis lineage is inconsistent")
            if evaluation["contract_id"] != allocation.contract_id:
                raise ValueError("portfolio allocation contract lineage is inconsistent")
            if evaluation["belief_state_version"] != allocation.belief_state_version:
                raise ValueError("portfolio allocation belief version lineage is inconsistent")
            if evaluation["current_tier"] != allocation.current_tier.value:
                raise ValueError("portfolio allocation tier lineage is inconsistent")
            if evaluation["recommendation"] != allocation.recommendation.value:
                raise ValueError("portfolio allocation recommendation lineage is inconsistent")

    def get(self, plan_id: UUID) -> PortfolioPlan | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM portfolio_plan WHERE id = %s",
                (plan_id,),
            ).fetchone()
            if row is None:
                return None
            return self._plan_from_row(conn, row)

    def get_by_idempotency_key(self, key: str) -> PortfolioPlan | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            return self._load_by_idempotency(conn, key)

    def _load_by_idempotency(
        self,
        conn: psycopg.Connection[dict[str, Any]],
        key: str,
    ) -> PortfolioPlan | None:
        row = conn.execute(
            "SELECT * FROM portfolio_plan WHERE idempotency_key = %s",
            (key,),
        ).fetchone()
        if row is None:
            return None
        return self._plan_from_row(conn, row)

    @staticmethod
    def _plan_from_row(
        conn: psycopg.Connection[dict[str, Any]],
        row: dict[str, Any],
    ) -> PortfolioPlan:
        allocation_rows = conn.execute(
            """
            SELECT * FROM portfolio_allocation
            WHERE plan_id = %s
            ORDER BY id
            """,
            (row["id"],),
        ).fetchall()
        allocations: list[PortfolioAllocation] = []
        for allocation in allocation_rows:
            capital = None
            if allocation["capital_amount"] is not None:
                capital = CapitalRequirement(
                    amount=allocation["capital_amount"],
                    currency=allocation["capital_currency"],
                    category=allocation["capital_category"],
                )
            allocations.append(
                PortfolioAllocation(
                    id=allocation["id"],
                    candidate_id=allocation["candidate_id"],
                    family_evaluation_id=allocation["family_evaluation_id"],
                    hypothesis_id=allocation["hypothesis_id"],
                    contract_id=allocation["contract_id"],
                    belief_state_version=allocation["belief_state_version"],
                    current_tier=allocation["current_tier"],
                    recommendation=allocation["recommendation"],
                    roles=tuple(allocation["roles"]),
                    group_key=allocation["group_key"],
                    resource_demand=ResourceVector.model_validate(allocation["resource_demand"]),
                    value=PortfolioValueEstimate.model_validate(allocation["value_estimate"]),
                    risk=RiskAssessment.model_validate(allocation["risk_assessment"]),
                    capital_requirement=capital,
                    utility=allocation["utility"],
                    scarcity_pressure=allocation["scarcity_pressure"],
                    rationale=allocation["rationale"],
                )
            )

        evaluations = [
            PortfolioCandidateEvaluation.model_validate(item)
            for item in row["evaluations"]
        ]
        return PortfolioPlan(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            policy_parameters=row["policy_parameters"],
            available_resources=ResourceVector.model_validate(row["available_resources"]),
            evaluations=evaluations,
            allocations=allocations,
            created_at=row["created_at"],
        )
