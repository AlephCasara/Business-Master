from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.capital import (
    CapitalAuthorization,
    CapitalAuthorizationRequest,
    CapitalAuthorizationStatus,
    CapitalEnvelope,
)
from business_master.domain.clock import utcnow
from business_master.policies.capital import CapitalPolicy


class CapitalAuthorizationError(RuntimeError):
    """Base error for durable capital-authorization failures."""


class CapitalAuthorizationDeniedError(CapitalAuthorizationError):
    """Raised when deterministic capital policy denies the request."""


class CapitalAuthorizationConflictError(CapitalAuthorizationError):
    """Raised when an idempotency key is reused with different semantics."""


class CapitalAuthorizationNotFoundError(CapitalAuthorizationError):
    def __init__(self, authorization_id: UUID) -> None:
        self.authorization_id = authorization_id
        super().__init__(f"unknown capital authorization: {authorization_id}")


class CapitalAuthorizationNotDueError(CapitalAuthorizationError):
    """Raised when explicit expiry is requested before the authorization is due."""


class CapitalAuthorizationStateError(CapitalAuthorizationError):
    """Raised for an invalid lifecycle transition."""


class PostgresCapitalAuthorizationStore:
    """Currency-serialized capital authorization over ledger-derived cash."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def authorize(
        self,
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
        *,
        policy: CapitalPolicy | None = None,
    ) -> CapitalAuthorization:
        effective_policy = policy or CapitalPolicy()
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            # Currency lock serializes competing claims on the same ledger cash.
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"capital:{request.currency}",),
            )
            self._expire_due(conn, request.requested_at, request.currency)

            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"capital-idempotency:{request.idempotency_key}",),
            )
            existing = self._load_by_idempotency(conn, request.idempotency_key)
            if existing is not None:
                self._assert_same_request(
                    existing,
                    request,
                    envelope,
                    effective_policy,
                )
                return existing

            self._validate_allocation(conn, request)
            active_for_allocation = conn.execute(
                """
                SELECT id
                FROM capital_authorization
                WHERE portfolio_allocation_id = %s AND status = 'active'
                LIMIT 1
                """,
                (request.portfolio_allocation_id,),
            ).fetchone()
            if active_for_allocation is not None:
                raise CapitalAuthorizationConflictError(
                    "portfolio allocation already has an active capital authorization"
                )

            ledger_cash = self._ledger_cash(conn, request.currency)
            active_outstanding = self._active_outstanding(conn, request.currency)
            period_committed = self._period_committed(conn, request, envelope)
            assessment = effective_policy.assess(
                request,
                envelope,
                ledger_cash=ledger_cash,
                active_outstanding=active_outstanding,
                period_committed=period_committed,
            )
            if not assessment.authorized:
                raise CapitalAuthorizationDeniedError(assessment.rationale)

            authorization = CapitalAuthorization(
                id=CapitalAuthorization.deterministic_id(request.idempotency_key),
                idempotency_key=request.idempotency_key,
                portfolio_allocation_id=request.portfolio_allocation_id,
                family_evaluation_id=request.family_evaluation_id,
                hypothesis_id=request.hypothesis_id,
                amount=request.amount,
                currency=request.currency,
                category=request.category,
                stage=request.stage,
                risk=request.risk,
                policy_name=effective_policy.name,
                policy_version=effective_policy.version,
                envelope=envelope,
                ledger_cash_at_authorization=assessment.ledger_cash,
                active_outstanding_before=assessment.active_outstanding,
                period_committed_before=assessment.period_committed,
                status=CapitalAuthorizationStatus.ACTIVE,
                rationale=assessment.rationale,
                authorized_at=request.requested_at,
                expires_at=request.expires_at,
            )
            conn.execute(
                """
                INSERT INTO capital_authorization (
                    id, idempotency_key, portfolio_allocation_id,
                    family_evaluation_id, hypothesis_id, amount, currency,
                    category, stage, risk, policy_name, policy_version, envelope,
                    ledger_cash_at_authorization, active_outstanding_before,
                    period_committed_before, status, rationale, authorized_at,
                    expires_at, consumed_at, released_at, expired_at,
                    ledger_transaction_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    authorization.id,
                    authorization.idempotency_key,
                    authorization.portfolio_allocation_id,
                    authorization.family_evaluation_id,
                    authorization.hypothesis_id,
                    authorization.amount,
                    authorization.currency,
                    authorization.category.value,
                    authorization.stage.value,
                    authorization.risk.value,
                    authorization.policy_name,
                    authorization.policy_version,
                    Jsonb(authorization.envelope.model_dump(mode="json")),
                    authorization.ledger_cash_at_authorization,
                    authorization.active_outstanding_before,
                    authorization.period_committed_before,
                    authorization.status.value,
                    authorization.rationale,
                    authorization.authorized_at,
                    authorization.expires_at,
                    authorization.consumed_at,
                    authorization.released_at,
                    authorization.expired_at,
                    authorization.ledger_transaction_id,
                ),
            )
            return authorization

    @staticmethod
    def _validate_allocation(
        conn: psycopg.Connection[dict[str, Any]],
        request: CapitalAuthorizationRequest,
    ) -> None:
        row = conn.execute(
            """
            SELECT family_evaluation_id, hypothesis_id,
                   capital_amount, capital_currency, capital_category
            FROM portfolio_allocation
            WHERE id = %s
            """,
            (request.portfolio_allocation_id,),
        ).fetchone()
        if row is None:
            raise ValueError("capital authorization portfolio allocation does not exist")
        if row["family_evaluation_id"] != request.family_evaluation_id:
            raise ValueError("capital authorization family-evaluation lineage is inconsistent")
        if row["hypothesis_id"] != request.hypothesis_id:
            raise ValueError("capital authorization hypothesis lineage is inconsistent")
        if row["capital_amount"] is None:
            raise ValueError("portfolio allocation declares no capital requirement")
        if Decimal(row["capital_amount"]) != request.amount:
            raise ValueError("capital request amount differs from portfolio allocation")
        if str(row["capital_currency"]).strip() != request.currency:
            raise ValueError("capital request currency differs from portfolio allocation")
        if row["capital_category"] != request.category.value:
            raise ValueError("capital request category differs from portfolio allocation")

    @staticmethod
    def _ledger_cash(
        conn: psycopg.Connection[dict[str, Any]],
        currency: str,
    ) -> Decimal:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(
                CASE WHEN side = 'debit' THEN amount ELSE -amount END
            ), 0) AS cash
            FROM economic_ledger_posting
            WHERE account = 'cash' AND currency = %s
            """,
            (currency,),
        ).fetchone()
        return Decimal(0) if row is None else Decimal(row["cash"])

    @staticmethod
    def _active_outstanding(
        conn: psycopg.Connection[dict[str, Any]],
        currency: str,
    ) -> Decimal:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS amount
            FROM capital_authorization
            WHERE currency = %s AND status = 'active'
            """,
            (currency,),
        ).fetchone()
        return Decimal(0) if row is None else Decimal(row["amount"])

    @staticmethod
    def _period_committed(
        conn: psycopg.Connection[dict[str, Any]],
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
    ) -> Decimal:
        if envelope.operator_hard_ceiling is None:
            return Decimal(0)
        if envelope.period_start is None or envelope.period_end is None:
            return Decimal(0)
        row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS amount
            FROM capital_authorization
            WHERE currency = %s
              AND category = %s
              AND status IN ('active', 'consumed')
              AND authorized_at >= %s
              AND authorized_at < %s
            """,
            (
                request.currency,
                request.category.value,
                envelope.period_start,
                envelope.period_end,
            ),
        ).fetchone()
        return Decimal(0) if row is None else Decimal(row["amount"])

    def get(self, authorization_id: UUID) -> CapitalAuthorization | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM capital_authorization WHERE id = %s",
                (authorization_id,),
            ).fetchone()
            return None if row is None else self._from_row(row)

    def get_by_idempotency_key(self, key: str) -> CapitalAuthorization | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            return self._load_by_idempotency(conn, key)

    def release(self, authorization_id: UUID) -> CapitalAuthorization:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM capital_authorization WHERE id = %s FOR UPDATE",
                (authorization_id,),
            ).fetchone()
            if row is None:
                raise CapitalAuthorizationNotFoundError(authorization_id)
            authorization = self._from_row(row)
            if authorization.status in {
                CapitalAuthorizationStatus.RELEASED,
                CapitalAuthorizationStatus.EXPIRED,
            }:
                return authorization
            if authorization.status is CapitalAuthorizationStatus.CONSUMED:
                raise CapitalAuthorizationStateError("consumed capital cannot be released")

            released_at = utcnow()
            conn.execute(
                """
                UPDATE capital_authorization
                SET status = 'released', released_at = %s
                WHERE id = %s
                """,
                (released_at, authorization_id),
            )
            return authorization.model_copy(
                update={
                    "status": CapitalAuthorizationStatus.RELEASED,
                    "released_at": released_at,
                }
            )

    def expire(
        self,
        authorization_id: UUID,
        *,
        as_of: datetime | None = None,
    ) -> CapitalAuthorization:
        effective_time = as_of or utcnow()
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM capital_authorization WHERE id = %s FOR UPDATE",
                (authorization_id,),
            ).fetchone()
            if row is None:
                raise CapitalAuthorizationNotFoundError(authorization_id)
            authorization = self._from_row(row)
            if authorization.status is not CapitalAuthorizationStatus.ACTIVE:
                return authorization
            if authorization.expires_at is None or authorization.expires_at > effective_time:
                raise CapitalAuthorizationNotDueError(
                    f"capital authorization {authorization_id} is not due for expiry"
                )

            conn.execute(
                """
                UPDATE capital_authorization
                SET status = 'expired', released_at = %s, expired_at = %s
                WHERE id = %s
                """,
                (effective_time, effective_time, authorization_id),
            )
            return authorization.model_copy(
                update={
                    "status": CapitalAuthorizationStatus.EXPIRED,
                    "released_at": effective_time,
                    "expired_at": effective_time,
                }
            )

    def expire_due(
        self,
        *,
        as_of: datetime | None = None,
        currency: str | None = None,
    ) -> int:
        effective_time = as_of or utcnow()
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            return self._expire_due(conn, effective_time, currency)

    def consume(
        self,
        authorization_id: UUID,
        ledger_transaction_id: UUID,
        *,
        as_of: datetime | None = None,
    ) -> CapitalAuthorization:
        consumed_at = as_of or utcnow()
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM capital_authorization WHERE id = %s FOR UPDATE",
                (authorization_id,),
            ).fetchone()
            if row is None:
                raise CapitalAuthorizationNotFoundError(authorization_id)
            authorization = self._from_row(row)
            if authorization.status is CapitalAuthorizationStatus.CONSUMED:
                if authorization.ledger_transaction_id != ledger_transaction_id:
                    raise CapitalAuthorizationStateError(
                        "capital authorization was consumed by a different ledger transaction"
                    )
                return authorization
            if authorization.status is not CapitalAuthorizationStatus.ACTIVE:
                raise CapitalAuthorizationStateError(
                    "only active capital authorization can be consumed"
                )
            if authorization.expires_at is not None and authorization.expires_at <= consumed_at:
                conn.execute(
                    """
                    UPDATE capital_authorization
                    SET status = 'expired', released_at = %s, expired_at = %s
                    WHERE id = %s
                    """,
                    (consumed_at, consumed_at, authorization_id),
                )
                return authorization.model_copy(
                    update={
                        "status": CapitalAuthorizationStatus.EXPIRED,
                        "released_at": consumed_at,
                        "expired_at": consumed_at,
                    }
                )

            transaction = conn.execute(
                "SELECT id FROM economic_ledger_transaction WHERE id = %s",
                (ledger_transaction_id,),
            ).fetchone()
            if transaction is None:
                raise ValueError("capital consumption ledger transaction does not exist")
            posting = conn.execute(
                """
                SELECT 1
                FROM economic_ledger_posting
                WHERE transaction_id = %s AND currency = %s
                LIMIT 1
                """,
                (ledger_transaction_id, authorization.currency),
            ).fetchone()
            if posting is None:
                raise ValueError("capital consumption ledger transaction currency is inconsistent")

            conn.execute(
                """
                UPDATE capital_authorization
                SET status = 'consumed', consumed_at = %s, ledger_transaction_id = %s
                WHERE id = %s
                """,
                (consumed_at, ledger_transaction_id, authorization_id),
            )
            return authorization.model_copy(
                update={
                    "status": CapitalAuthorizationStatus.CONSUMED,
                    "consumed_at": consumed_at,
                    "ledger_transaction_id": ledger_transaction_id,
                }
            )

    @staticmethod
    def _expire_due(
        conn: psycopg.Connection[dict[str, Any]],
        as_of: datetime,
        currency: str | None,
    ) -> int:
        if currency is None:
            cursor = conn.execute(
                """
                UPDATE capital_authorization
                SET status = 'expired', released_at = %s, expired_at = %s
                WHERE status = 'active'
                  AND expires_at IS NOT NULL
                  AND expires_at <= %s
                """,
                (as_of, as_of, as_of),
            )
        else:
            cursor = conn.execute(
                """
                UPDATE capital_authorization
                SET status = 'expired', released_at = %s, expired_at = %s
                WHERE status = 'active'
                  AND currency = %s
                  AND expires_at IS NOT NULL
                  AND expires_at <= %s
                """,
                (as_of, as_of, currency, as_of),
            )
        return int(cursor.rowcount)

    def _load_by_idempotency(
        self,
        conn: psycopg.Connection[dict[str, Any]],
        key: str,
    ) -> CapitalAuthorization | None:
        row = conn.execute(
            "SELECT * FROM capital_authorization WHERE idempotency_key = %s",
            (key,),
        ).fetchone()
        return None if row is None else self._from_row(row)

    @staticmethod
    def _assert_same_request(
        authorization: CapitalAuthorization,
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
        policy: CapitalPolicy,
    ) -> None:
        if (
            authorization.portfolio_allocation_id != request.portfolio_allocation_id
            or authorization.family_evaluation_id != request.family_evaluation_id
            or authorization.hypothesis_id != request.hypothesis_id
            or authorization.amount != request.amount
            or authorization.currency != request.currency
            or authorization.category is not request.category
            or authorization.stage is not request.stage
            or authorization.risk is not request.risk
            or authorization.authorized_at != request.requested_at
            or authorization.expires_at != request.expires_at
            or authorization.envelope != envelope
            or authorization.policy_name != policy.name
            or authorization.policy_version != policy.version
        ):
            raise CapitalAuthorizationConflictError(
                "capital idempotency key was reused with different semantics"
            )

    @staticmethod
    def _from_row(row: dict[str, Any]) -> CapitalAuthorization:
        return CapitalAuthorization(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            portfolio_allocation_id=row["portfolio_allocation_id"],
            family_evaluation_id=row["family_evaluation_id"],
            hypothesis_id=row["hypothesis_id"],
            amount=Decimal(row["amount"]),
            currency=str(row["currency"]).strip(),
            category=row["category"],
            stage=row["stage"],
            risk=row["risk"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            envelope=CapitalEnvelope.model_validate(row["envelope"]),
            ledger_cash_at_authorization=Decimal(row["ledger_cash_at_authorization"]),
            active_outstanding_before=Decimal(row["active_outstanding_before"]),
            period_committed_before=Decimal(row["period_committed_before"]),
            status=row["status"],
            rationale=row["rationale"],
            authorized_at=row["authorized_at"],
            expires_at=row["expires_at"],
            consumed_at=row["consumed_at"],
            released_at=row["released_at"],
            expired_at=row["expired_at"],
            ledger_transaction_id=row["ledger_transaction_id"],
        )
