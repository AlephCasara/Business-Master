from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.experiment_contracts import (
    ExperimentContract,
    ExperimentContractBinding,
)


class PostgresExperimentContractStore:
    """PostgreSQL adapter for immutable V2 experiment contracts."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save_contract(self, contract: ExperimentContract) -> None:
        payload = contract.model_dump(mode="json")
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            inserted = conn.execute(
                """
                INSERT INTO experiment_contract (
                    id, economic_hypothesis_id, business_family, question,
                    intervention_dimensions, held_constant_dimensions,
                    expected_observation, falsification_condition, measurement,
                    resource_requirements, budget, parent_contract_id,
                    supersedes_contract_id, origin_decision_id, contract_version, created_at
                ) VALUES (
                    %(id)s, %(economic_hypothesis_id)s, %(business_family)s, %(question)s,
                    %(intervention_dimensions)s, %(held_constant_dimensions)s,
                    %(expected_observation)s, %(falsification_condition)s,
                    %(measurement)s, %(resource_requirements)s, %(budget)s,
                    %(parent_contract_id)s, %(supersedes_contract_id)s,
                    %(origin_decision_id)s, %(contract_version)s, %(created_at)s
                )
                ON CONFLICT (id) DO NOTHING
                RETURNING id
                """,
                {
                    "id": contract.id,
                    "economic_hypothesis_id": contract.economic_hypothesis_id,
                    "business_family": contract.business_family,
                    "question": contract.question,
                    "intervention_dimensions": Jsonb(payload["intervention_dimensions"]),
                    "held_constant_dimensions": contract.held_constant_dimensions,
                    "expected_observation": contract.expected_observation,
                    "falsification_condition": contract.falsification_condition,
                    "measurement": Jsonb(payload["measurement"]),
                    "resource_requirements": Jsonb(
                        payload["resource_requirements"]["quantities"]
                    ),
                    "budget": Jsonb(payload["budget"]),
                    "parent_contract_id": contract.parent_contract_id,
                    "supersedes_contract_id": contract.supersedes_contract_id,
                    "origin_decision_id": contract.origin_decision_id,
                    "contract_version": contract.contract_version,
                    "created_at": contract.created_at,
                },
            ).fetchone()
            if inserted is not None:
                return

            row = conn.execute(
                "SELECT * FROM experiment_contract WHERE id = %s",
                (contract.id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("experiment contract conflict could not be reloaded")
            persisted = self._contract_from_row(row)
            if persisted != contract:
                raise ValueError("experiment contract is immutable once persisted")

    def get_contract(self, contract_id: UUID) -> ExperimentContract | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM experiment_contract WHERE id = %s",
                (contract_id,),
            ).fetchone()
        if row is None:
            return None
        return self._contract_from_row(row)

    def bind_experiment(self, binding: ExperimentContractBinding) -> None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            inserted = conn.execute(
                """
                INSERT INTO experiment_contract_binding (experiment_id, contract_id, bound_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (experiment_id) DO NOTHING
                RETURNING experiment_id, contract_id, bound_at
                """,
                (binding.experiment_id, binding.contract_id, binding.bound_at),
            ).fetchone()
            if inserted is not None:
                return

            row = conn.execute(
                """
                SELECT experiment_id, contract_id, bound_at
                FROM experiment_contract_binding
                WHERE experiment_id = %s
                """,
                (binding.experiment_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("experiment contract binding conflict could not be reloaded")
            if row["contract_id"] != binding.contract_id:
                raise ValueError("an experiment cannot be rebound to a different contract")

    def get_binding(self, experiment_id: UUID) -> ExperimentContractBinding | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                """
                SELECT experiment_id, contract_id, bound_at
                FROM experiment_contract_binding
                WHERE experiment_id = %s
                """,
                (experiment_id,),
            ).fetchone()
        if row is None:
            return None
        return ExperimentContractBinding(**row)

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
            resource_requirements={"quantities": row["resource_requirements"]},
            budget=row["budget"],
            parent_contract_id=row["parent_contract_id"],
            supersedes_contract_id=row["supersedes_contract_id"],
            origin_decision_id=row["origin_decision_id"],
            contract_version=row["contract_version"],
            created_at=row["created_at"],
        )
