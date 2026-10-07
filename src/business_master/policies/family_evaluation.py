from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from uuid import UUID

from business_master.domain.belief_updates import EvidenceInterpretation
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTier,
    MetricAggregation,
)
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.experiment_contracts import MetricCriterion
from business_master.domain.family_evaluation import (
    BusinessFamily,
    CriterionEvaluation,
    CriterionRole,
    EvaluationRecommendation,
    EvidenceInterpretationDecision,
    FamilyEvaluation,
    FamilyEvaluationRequest,
    ReadinessStatus,
)
from business_master.domain.ledger import EconomicLedgerSnapshot

_DECISION_GRADE_OBSERVED_PROVENANCE = {
    EvidenceProvenance.OBSERVED_OWN,
    EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL,
    EvidenceProvenance.OBSERVED_PUBLIC,
}


@dataclass(frozen=True, slots=True)
class FamilyGateProfile:
    probe_replications: int
    scale_replications: int
    scale_contexts: int
    probe_min_independent_sources: int = 1
    probe_requires_operational_ready: bool = False
    scale_requires_operational_ready: bool = True
    scale_requires_economic_ready: bool = False


class FamilyEvaluationPolicy:
    name = "family_evaluation"
    version = "2"
    family: BusinessFamily
    profile: FamilyGateProfile

    def evaluate(self, request: FamilyEvaluationRequest) -> FamilyEvaluation:
        self._validate_family(request)
        decision_grade_ids = self._decision_grade_evidence_ids(request.evidence)
        decision_grade_evidence = tuple(
            record for record in request.evidence if record.id in decision_grade_ids
        )
        criteria = self._evaluate_criteria(request, decision_grade_evidence)
        interpretations = self._interpret_evidence(
            request.evidence,
            criteria,
            decision_grade_ids,
        )

        # Replication/sufficiency counts primary external observations only. Derived
        # calculated metrics may satisfy criteria when their lineage is decision-grade,
        # but they must not manufacture additional observations or independence.
        external_records = [
            record
            for record in decision_grade_evidence
            if record.evidence_class in {EvidenceClass.MARKET, EvidenceClass.ECONOMIC}
            and record.provenance in _DECISION_GRADE_OBSERVED_PROVENANCE
        ]
        independent_sources = len(
            {self._independence_key(record) for record in external_records}
        )
        external_observations = len(external_records)
        required = request.hypothesis.evidence_requirements
        required_kinds_present = {record.kind for record in decision_grade_evidence}

        evidence_sufficient = (
            external_observations >= request.contract.measurement.minimum_external_observations
            and external_observations >= required.minimum_count
            and independent_sources >= required.minimum_independent_sources
            and set(required.required_kinds).issubset(required_kinds_present)
        )

        supporting_met = any(
            item.role is CriterionRole.SUPPORTING and item.met for item in criteria
        )
        falsifying_met = any(
            item.role is CriterionRole.FALSIFYING and item.met for item in criteria
        )
        conflicting = supporting_met and falsifying_met
        supporting_signal = supporting_met and not falsifying_met
        falsified = falsifying_met and not supporting_met

        economic_readiness = self._economic_readiness(request.economic_snapshot)
        operational_readiness = self._operational_readiness(request)
        recommendation, rationale = self._recommend(
            request=request,
            evidence_sufficient=evidence_sufficient,
            supporting_signal=supporting_signal,
            falsified=falsified,
            conflicting=conflicting,
            independent_sources=independent_sources,
            economic_readiness=economic_readiness,
            operational_readiness=operational_readiness,
        )

        return FamilyEvaluation(
            id=FamilyEvaluation.deterministic_id(request.idempotency_key),
            idempotency_key=request.idempotency_key,
            family=self.family,
            hypothesis_id=request.hypothesis.id,
            contract_id=request.contract.id,
            belief_state_version=request.belief_state.state_version,
            current_tier=request.current_tier,
            policy_name=f"{self.name}:{self.family.value}",
            policy_version=self.version,
            evidence_ids=[record.id for record in request.evidence],
            interpretations=interpretations,
            criteria=criteria,
            external_observations=external_observations,
            independent_sources=independent_sources,
            replication_count=request.context.replication_count,
            distinct_contexts=request.context.distinct_contexts,
            evidence_sufficient=evidence_sufficient,
            supporting_signal=supporting_signal,
            falsified=falsified,
            economic_readiness=economic_readiness,
            operational_readiness=operational_readiness,
            recommendation=recommendation,
            rationale=rationale,
            evaluated_at=request.evaluated_at,
        )

    def _validate_family(self, request: FamilyEvaluationRequest) -> None:
        if request.contract.business_family != self.family.value:
            raise ValueError(
                f"{self.family.value} policy cannot evaluate "
                f"{request.contract.business_family!r} contract"
            )

    def _independence_key(self, record: EvidenceRecord) -> str:
        """Return the identity used for independent-source requirements.

        New adapters should provide ``independence_key`` when collection source and
        economically independent entity are different concepts. ``source`` remains a
        compatibility fallback for existing evidence.
        """

        if record.independence_key is not None:
            return f"independence:{record.independence_key}"
        return f"source:{record.source}"

    @staticmethod
    def _decision_grade_evidence_ids(
        evidence: tuple[EvidenceRecord, ...],
    ) -> set[UUID]:
        """Return evidence safe to use for economic/market policy decisions.

        Direct observations are admissible when their provenance is observed own,
        official external, or public. Calculated evidence is admissible only when all
        of its declared inputs are present in this evaluation and are themselves
        decision-grade. Inferred, creator-claim, unknown, and calculated evidence
        with incomplete/weak lineage cannot be laundered into progression evidence.
        """

        by_id = {record.id: record for record in evidence}
        cache: dict[UUID, bool] = {}

        def admissible(record: EvidenceRecord, visiting: set[UUID]) -> bool:
            cached = cache.get(record.id)
            if cached is not None:
                return cached
            if record.id in visiting:
                cache[record.id] = False
                return False
            if record.provenance in _DECISION_GRADE_OBSERVED_PROVENANCE:
                cache[record.id] = True
                return True
            if record.provenance is not EvidenceProvenance.CALCULATED:
                cache[record.id] = False
                return False

            parents = [by_id.get(input_id) for input_id in record.input_evidence_ids]
            if not parents or any(parent is None for parent in parents):
                cache[record.id] = False
                return False
            next_visiting = {*visiting, record.id}
            result = all(
                parent is not None and admissible(parent, next_visiting)
                for parent in parents
            )
            cache[record.id] = result
            return result

        return {record.id for record in evidence if admissible(record, set())}

    def _evaluate_criteria(
        self,
        request: FamilyEvaluationRequest,
        evidence: tuple[EvidenceRecord, ...],
    ) -> list[CriterionEvaluation]:
        result: list[CriterionEvaluation] = []
        for role, criteria in (
            (CriterionRole.SUPPORTING, request.contract.measurement.supporting_criteria),
            (CriterionRole.FALSIFYING, request.contract.measurement.falsifying_criteria),
        ):
            for criterion in criteria:
                result.append(self._evaluate_criterion(role, criterion, evidence))
        return result

    @staticmethod
    def _evaluate_criterion(
        role: CriterionRole,
        criterion: MetricCriterion,
        evidence: tuple[EvidenceRecord, ...],
    ) -> CriterionEvaluation:
        observations: list[tuple[EvidenceRecord, float]] = []
        for record in evidence:
            if record.evidence_class is not criterion.evidence_class:
                continue
            raw = record.features.get(criterion.metric)
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                continue
            observations.append((record, float(raw)))

        aggregated: float | None = None
        if len(observations) >= criterion.minimum_observations:
            values = [value for _, value in observations]
            if criterion.aggregation is MetricAggregation.LATEST:
                latest = max(observations, key=lambda item: item[0].observed_at)
                aggregated = latest[1]
            elif criterion.aggregation is MetricAggregation.SUM:
                aggregated = sum(values)
            elif criterion.aggregation is MetricAggregation.MEAN:
                aggregated = fmean(values)
            elif criterion.aggregation is MetricAggregation.MIN:
                aggregated = min(values)
            elif criterion.aggregation is MetricAggregation.MAX:
                aggregated = max(values)
            else:
                raise ValueError(f"unsupported aggregation: {criterion.aggregation}")

        met = aggregated is not None and FamilyEvaluationPolicy._compare(
            aggregated,
            criterion.operator,
            criterion.threshold,
        )
        return CriterionEvaluation(
            role=role,
            metric=criterion.metric,
            evidence_class=criterion.evidence_class.value,
            aggregation=criterion.aggregation.value,
            operator=criterion.operator.value,
            threshold=criterion.threshold,
            observation_count=len(observations),
            aggregated_value=aggregated,
            met=met,
            evidence_ids=[record.id for record, _ in observations],
        )

    @staticmethod
    def _compare(value: float, operator: ComparisonOperator, threshold: float) -> bool:
        if operator is ComparisonOperator.LT:
            return value < threshold
        if operator is ComparisonOperator.LTE:
            return value <= threshold
        if operator is ComparisonOperator.EQ:
            return value == threshold
        if operator is ComparisonOperator.GTE:
            return value >= threshold
        if operator is ComparisonOperator.GT:
            return value > threshold
        raise ValueError(f"unsupported comparison operator: {operator}")

    @staticmethod
    def _interpret_evidence(
        evidence: tuple[EvidenceRecord, ...],
        criteria: list[CriterionEvaluation],
        decision_grade_ids: set[UUID],
    ) -> list[EvidenceInterpretationDecision]:
        supporting_weights: dict[UUID, float] = {}
        falsifying_weights: dict[UUID, float] = {}

        for criterion in criteria:
            if not criterion.met or not criterion.evidence_ids:
                continue
            weight = 1.0 / len(criterion.evidence_ids)
            target = (
                supporting_weights
                if criterion.role is CriterionRole.SUPPORTING
                else falsifying_weights
            )
            for evidence_id in criterion.evidence_ids:
                target[evidence_id] = max(target.get(evidence_id, 0.0), weight)

        result: list[EvidenceInterpretationDecision] = []
        for record in evidence:
            if record.evidence_class is EvidenceClass.TECHNICAL:
                result.append(
                    EvidenceInterpretationDecision(
                        evidence_id=record.id,
                        interpretation=EvidenceInterpretation.TECHNICAL,
                        strength=1.0,
                        rationale="Technical evidence is operational, not economic falsification.",
                    )
                )
                continue

            if record.id not in decision_grade_ids:
                result.append(
                    EvidenceInterpretationDecision(
                        evidence_id=record.id,
                        interpretation=EvidenceInterpretation.NEUTRAL,
                        strength=1.0,
                        rationale=(
                            "Evidence provenance/lineage is not decision-grade for "
                            "market or economic progression."
                        ),
                    )
                )
                continue

            support = supporting_weights.get(record.id, 0.0)
            falsify = falsifying_weights.get(record.id, 0.0)
            if support > 0.0 and falsify > 0.0:
                interpretation = EvidenceInterpretation.NEUTRAL
                strength = max(support, falsify)
                rationale = "Evidence contributes to conflicting met contract criteria."
            elif support > 0.0:
                interpretation = EvidenceInterpretation.SUPPORTING
                strength = support
                rationale = "Evidence contributes to a met supporting contract criterion."
            elif falsify > 0.0:
                interpretation = EvidenceInterpretation.FALSIFYING
                strength = falsify
                rationale = "Evidence contributes to a met falsifying contract criterion."
            else:
                interpretation = EvidenceInterpretation.NEUTRAL
                strength = 1.0
                rationale = "Evidence does not contribute to a met contract criterion."

            result.append(
                EvidenceInterpretationDecision(
                    evidence_id=record.id,
                    interpretation=interpretation,
                    strength=strength,
                    rationale=rationale,
                )
            )
        return result

    @staticmethod
    def _economic_readiness(
        snapshot: EconomicLedgerSnapshot | None,
    ) -> ReadinessStatus:
        if snapshot is None:
            return ReadinessStatus.UNKNOWN
        if snapshot.contribution_after_acquisition > 0:
            return ReadinessStatus.READY
        has_economic_activity = any(
            value != 0
            for value in (
                snapshot.recognized_revenue,
                snapshot.refunds_returns,
                snapshot.fees,
                snapshot.direct_costs,
                snapshot.acquisition_spend,
                snapshot.receivables,
                snapshot.payables,
                snapshot.working_capital_exposure,
            )
        )
        return ReadinessStatus.NOT_READY if has_economic_activity else ReadinessStatus.UNKNOWN

    @staticmethod
    def _operational_readiness(request: FamilyEvaluationRequest) -> ReadinessStatus:
        context = request.context
        if context.severe_risk_events > 0 or context.operational_failures > 0:
            return ReadinessStatus.NOT_READY
        if context.operational_successes > 0:
            return ReadinessStatus.READY
        return ReadinessStatus.UNKNOWN

    def _recommend(
        self,
        *,
        request: FamilyEvaluationRequest,
        evidence_sufficient: bool,
        supporting_signal: bool,
        falsified: bool,
        conflicting: bool,
        independent_sources: int,
        economic_readiness: ReadinessStatus,
        operational_readiness: ReadinessStatus,
    ) -> tuple[EvaluationRecommendation, str]:
        if request.context.severe_risk_events > 0:
            return (
                EvaluationRecommendation.PAUSE,
                "Severe risk evidence blocks further family progression.",
            )
        if conflicting:
            return (
                EvaluationRecommendation.CONTINUE,
                "Supporting and falsifying criteria are both met; collect discriminating evidence.",
            )
        if falsified and evidence_sufficient:
            return (
                EvaluationRecommendation.REJECT,
                "Sufficient family evidence meets falsification criteria without support.",
            )
        if not evidence_sufficient:
            return (
                EvaluationRecommendation.INSUFFICIENT_EVIDENCE,
                "Evidence has not met the contract and hypothesis sufficiency requirements.",
            )
        if not supporting_signal:
            return (
                EvaluationRecommendation.CONTINUE,
                "Evidence is sufficient to evaluate but does not yet support progression.",
            )

        if request.current_tier is EvidenceTier.PROBE and self._probe_gate(
            request,
            independent_sources=independent_sources,
            operational_readiness=operational_readiness,
        ):
            return (
                EvaluationRecommendation.GRADUATE,
                f"{self.family.value} probe clears family-specific pilot gates.",
            )

        if request.current_tier is EvidenceTier.PILOT and self._scale_gate(
            request,
            economic_readiness=economic_readiness,
            operational_readiness=operational_readiness,
        ):
            return (
                EvaluationRecommendation.GRADUATE,
                f"{self.family.value} pilot clears family-specific scale gates.",
            )

        return (
            EvaluationRecommendation.REPLICATE,
            (
                "Supporting evidence exists, but family progression gates require "
                "more replication/readiness."
            ),
        )

    def _probe_gate(
        self,
        request: FamilyEvaluationRequest,
        *,
        independent_sources: int,
        operational_readiness: ReadinessStatus,
    ) -> bool:
        required_sources = max(
            self.profile.probe_min_independent_sources,
            request.hypothesis.evidence_requirements.minimum_independent_sources,
        )
        if independent_sources < required_sources:
            return False
        if request.context.replication_count < self.profile.probe_replications:
            return False
        return not (
            self.profile.probe_requires_operational_ready
            and operational_readiness is not ReadinessStatus.READY
        )

    def _scale_gate(
        self,
        request: FamilyEvaluationRequest,
        *,
        economic_readiness: ReadinessStatus,
        operational_readiness: ReadinessStatus,
    ) -> bool:
        if request.context.replication_count < self.profile.scale_replications:
            return False
        if request.context.distinct_contexts < self.profile.scale_contexts:
            return False
        if (
            self.profile.scale_requires_operational_ready
            and operational_readiness is not ReadinessStatus.READY
        ):
            return False
        return not (
            self.profile.scale_requires_economic_ready
            and economic_readiness is not ReadinessStatus.READY
        )


class ContentEvaluationPolicy(FamilyEvaluationPolicy):
    family = BusinessFamily.CONTENT
    profile = FamilyGateProfile(
        probe_replications=1,
        scale_replications=2,
        scale_contexts=2,
        scale_requires_operational_ready=True,
    )


class B2BEvaluationPolicy(FamilyEvaluationPolicy):
    version = "3"
    family = BusinessFamily.B2B
    profile = FamilyGateProfile(
        probe_replications=1,
        scale_replications=2,
        scale_contexts=2,
        probe_min_independent_sources=2,
        scale_requires_operational_ready=True,
        scale_requires_economic_ready=True,
    )

    def _independence_key(self, record: EvidenceRecord) -> str:
        # Explicit adapter-provided identity is canonical. PR8 already taught B2B
        # policies to prefer an entity subject over transport/source, so preserve
        # that behavior for existing persisted records before falling back to source.
        if record.independence_key is not None:
            return super()._independence_key(record)
        if record.subject_type is not None and record.subject_id is not None:
            return f"subject:{record.subject_type}:{record.subject_id}"
        return super()._independence_key(record)


class CommerceEvaluationPolicy(FamilyEvaluationPolicy):
    family = BusinessFamily.COMMERCE
    profile = FamilyGateProfile(
        probe_replications=1,
        scale_replications=2,
        scale_contexts=2,
        scale_requires_operational_ready=True,
        scale_requires_economic_ready=True,
    )


class CapabilityEvaluationPolicy(FamilyEvaluationPolicy):
    family = BusinessFamily.CAPABILITY
    profile = FamilyGateProfile(
        probe_replications=1,
        scale_replications=2,
        scale_contexts=2,
        probe_requires_operational_ready=True,
        scale_requires_operational_ready=True,
    )


_POLICY_BY_FAMILY: dict[BusinessFamily, type[FamilyEvaluationPolicy]] = {
    BusinessFamily.CONTENT: ContentEvaluationPolicy,
    BusinessFamily.B2B: B2BEvaluationPolicy,
    BusinessFamily.COMMERCE: CommerceEvaluationPolicy,
    BusinessFamily.CAPABILITY: CapabilityEvaluationPolicy,
}


def policy_for_family(family: str | BusinessFamily) -> FamilyEvaluationPolicy:
    try:
        normalized = family if isinstance(family, BusinessFamily) else BusinessFamily(family)
    except ValueError as exc:
        raise ValueError(f"unsupported business family: {family!r}") from exc
    return _POLICY_BY_FAMILY[normalized]()
