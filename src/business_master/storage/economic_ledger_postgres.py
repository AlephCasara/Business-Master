from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.clock import utcnow
from business_master.domain.ledger import (
    EconomicLedgerSnapshot,
    LedgerAccount,
    LedgerPosting,
    LedgerSide,
    LedgerTransaction,
    LedgerTransactionRequest,
)


class EconomicLedgerError(RuntimeError):
    """Base error for deterministic economic-ledger failures."""


class LedgerTransactionConflictError(EconomicLedgerError):
    """Raised when an idempotency key is reused for a different transaction."""


class PostgresEconomicLedgerStore:
    """Append-only double-entry economic ledger backed by PostgreSQL."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def record(self, request: LedgerTransactionRequest) -> LedgerTransaction:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (request.idempotency_key,),
            )

            existing = self._load_by_idempotency(conn, request.idempotency_key)
            if existing is not None:
                self._assert_same_request(existing, request)
                return existing

            transaction = LedgerTransaction(
                id=uuid4(),
                idempotency_key=request.idempotency_key,
                occurred_at=request.occurred_at,
                recorded_at=utcnow(),
                description=request.description,
                postings=request.postings,
                experiment_id=request.experiment_id,
                offer_id=request.offer_id,
                channel_id=request.channel_id,
                external_ref=request.external_ref,
                metadata=request.metadata,
            )
            conn.execute(
                """
                INSERT INTO economic_ledger_transaction (
                    id, idempotency_key, occurred_at, recorded_at, description,
                    experiment_id, offer_id, channel_id, external_ref, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    transaction.id,
                    transaction.idempotency_key,
                    transaction.occurred_at,
                    transaction.recorded_at,
                    transaction.description,
                    transaction.experiment_id,
                    transaction.offer_id,
                    transaction.channel_id,
                    transaction.external_ref,
                    Jsonb(transaction.metadata),
                ),
            )
            for posting in transaction.postings:
                conn.execute(
                    """
                    INSERT INTO economic_ledger_posting (
                        id, transaction_id, account, side, amount, currency
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        transaction.id,
                        posting.account.value,
                        posting.side.value,
                        posting.amount,
                        posting.currency,
                    ),
                )
            return transaction

    def get(self, transaction_id: UUID) -> LedgerTransaction | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM economic_ledger_transaction WHERE id = %s",
                (transaction_id,),
            ).fetchone()
            if row is None:
                return None
            return self._transaction_from_row(conn, row)

    def list_transactions(
        self,
        *,
        currency: str | None = None,
        experiment_id: UUID | None = None,
        offer_id: UUID | None = None,
        channel_id: UUID | None = None,
    ) -> list[LedgerTransaction]:
        clauses: list[str] = []
        params: list[object] = []
        if currency is not None:
            normalized = self._normalize_currency(currency)
            clauses.append(
                "EXISTS (SELECT 1 FROM economic_ledger_posting p "
                "WHERE p.transaction_id = t.id AND p.currency = %s)"
            )
            params.append(normalized)
        if experiment_id is not None:
            clauses.append("t.experiment_id = %s")
            params.append(experiment_id)
        if offer_id is not None:
            clauses.append("t.offer_id = %s")
            params.append(offer_id)
        if channel_id is not None:
            clauses.append("t.channel_id = %s")
            params.append(channel_id)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = (
            "SELECT t.* FROM economic_ledger_transaction t "
            f"{where} ORDER BY t.occurred_at, t.id"
        )
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._transaction_from_row(conn, row) for row in rows]

    def snapshot(
        self,
        currency: str,
        *,
        experiment_id: UUID | None = None,
        offer_id: UUID | None = None,
        channel_id: UUID | None = None,
    ) -> EconomicLedgerSnapshot:
        normalized_currency = self._normalize_currency(currency)
        clauses = ["p.currency = %s"]
        params: list[object] = [normalized_currency]
        if experiment_id is not None:
            clauses.append("t.experiment_id = %s")
            params.append(experiment_id)
        if offer_id is not None:
            clauses.append("t.offer_id = %s")
            params.append(offer_id)
        if channel_id is not None:
            clauses.append("t.channel_id = %s")
            params.append(channel_id)

        query = f"""
            SELECT p.account, p.side, p.amount
            FROM economic_ledger_posting p
            JOIN economic_ledger_transaction t ON t.id = p.transaction_id
            WHERE {' AND '.join(clauses)}
        """
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(query, params).fetchall()

        debit_balances = {account: Decimal(0) for account in LedgerAccount}
        for row in rows:
            account = LedgerAccount(str(row["account"]))
            amount = Decimal(row["amount"])
            if LedgerSide(str(row["side"])) is LedgerSide.DEBIT:
                debit_balances[account] += amount
            else:
                debit_balances[account] -= amount

        cash = debit_balances[LedgerAccount.CASH]
        receivables = debit_balances[LedgerAccount.ACCOUNTS_RECEIVABLE]
        working_capital_assets = debit_balances[LedgerAccount.WORKING_CAPITAL_ASSET]
        payables = -debit_balances[LedgerAccount.ACCOUNTS_PAYABLE]
        revenue = -debit_balances[LedgerAccount.REVENUE]
        refunds = debit_balances[LedgerAccount.REFUNDS_RETURNS]
        fees = debit_balances[LedgerAccount.FEES]
        direct_costs = debit_balances[LedgerAccount.DIRECT_COSTS]
        acquisition_spend = debit_balances[LedgerAccount.ACQUISITION_SPEND]
        contribution_margin = revenue - refunds - fees - direct_costs

        return EconomicLedgerSnapshot(
            currency=normalized_currency,
            cash_available=cash,
            receivables=receivables,
            payables=payables,
            working_capital_assets=working_capital_assets,
            working_capital_exposure=receivables + working_capital_assets - payables,
            recognized_revenue=revenue,
            refunds_returns=refunds,
            fees=fees,
            direct_costs=direct_costs,
            acquisition_spend=acquisition_spend,
            contribution_margin=contribution_margin,
            contribution_after_acquisition=contribution_margin - acquisition_spend,
        )

    def _load_by_idempotency(
        self,
        conn: psycopg.Connection[dict[str, Any]],
        idempotency_key: str,
    ) -> LedgerTransaction | None:
        row = conn.execute(
            "SELECT * FROM economic_ledger_transaction WHERE idempotency_key = %s",
            (idempotency_key,),
        ).fetchone()
        if row is None:
            return None
        return self._transaction_from_row(conn, row)

    @classmethod
    def _transaction_from_row(
        cls,
        conn: psycopg.Connection[dict[str, Any]],
        row: dict[str, Any],
    ) -> LedgerTransaction:
        posting_rows = conn.execute(
            """
            SELECT account, side, amount, currency
            FROM economic_ledger_posting
            WHERE transaction_id = %s
            ORDER BY account, side, amount, id
            """,
            (row["id"],),
        ).fetchall()
        postings = tuple(
            LedgerPosting(
                account=posting["account"],
                side=posting["side"],
                amount=Decimal(posting["amount"]),
                currency=posting["currency"],
            )
            for posting in posting_rows
        )
        return LedgerTransaction(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            occurred_at=row["occurred_at"],
            recorded_at=row["recorded_at"],
            description=row["description"],
            postings=postings,
            experiment_id=row["experiment_id"],
            offer_id=row["offer_id"],
            channel_id=row["channel_id"],
            external_ref=row["external_ref"],
            metadata=row["metadata"],
        )

    @classmethod
    def _assert_same_request(
        cls,
        transaction: LedgerTransaction,
        request: LedgerTransactionRequest,
    ) -> None:
        if (
            transaction.occurred_at != request.occurred_at
            or transaction.description != request.description
            or transaction.experiment_id != request.experiment_id
            or transaction.offer_id != request.offer_id
            or transaction.channel_id != request.channel_id
            or transaction.external_ref != request.external_ref
            or transaction.metadata != request.metadata
            or cls._posting_signature(transaction.postings)
            != cls._posting_signature(request.postings)
        ):
            raise LedgerTransactionConflictError(
                "idempotency key already belongs to a different ledger transaction"
            )

    @staticmethod
    def _posting_signature(
        postings: tuple[LedgerPosting, ...],
    ) -> tuple[tuple[str, str, Decimal, str], ...]:
        return tuple(
            sorted(
                (
                    posting.account.value,
                    posting.side.value,
                    posting.amount,
                    posting.currency,
                )
                for posting in postings
            )
        )

    @staticmethod
    def _normalize_currency(currency: str) -> str:
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a 3-letter alphabetic code")
        return normalized
