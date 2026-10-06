from __future__ import annotations

from dataclasses import dataclass

from business_master.domain.models import OpportunityScore


@dataclass(frozen=True, slots=True)
class ScoringPolicy:
    """Pure scoring policy; no model calls and no side effects."""

    bootstrap_expected_value_weight: float = 0.15
    mature_expected_value_weight: float = 0.70
    uncertainty_bonus_weight: float = 0.10
    epsilon_cost: float = 1e-6

    def bootstrap_priority(self, score: OpportunityScore) -> float:
        """Prioritize learning when reliable revenue evidence is still sparse."""
        learning_value = (
            score.information_gain
            * score.feedback_speed
            * score.downstream_reuse
        )
        total_cost = (
            score.compute_cost
            + score.cash_cost
            + score.human_time_cost
            + self.epsilon_cost
        )
        return (
            learning_value / total_cost
            + self.bootstrap_expected_value_weight * max(score.expected_value, 0.0)
            + self.uncertainty_bonus_weight * score.uncertainty
        )

    def mature_priority(self, score: OpportunityScore) -> float:
        """Shift toward economics while preserving a bounded learning incentive."""
        learning_value = (
            score.information_gain
            * score.feedback_speed
            * score.downstream_reuse
        )
        total_cost = (
            score.compute_cost
            + score.cash_cost
            + score.human_time_cost
            + self.epsilon_cost
        )
        return (
            self.mature_expected_value_weight * score.expected_value
            + (1.0 - self.mature_expected_value_weight) * (learning_value / total_cost)
            + 0.5 * self.uncertainty_bonus_weight * score.uncertainty
        )
