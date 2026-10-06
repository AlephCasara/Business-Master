from uuid import uuid4

import pytest

from business_master.domain.enums import EvidenceTier
from business_master.policies.allocation import AllocationCandidate, AllocationPolicy


def test_allocator_preserves_exploration_capacity() -> None:
    probe = uuid4()
    winner = uuid4()
    policy = AllocationPolicy(exploration_fraction=0.20, max_candidate_fraction=0.80)

    allocations = policy.allocate(
        [
            AllocationCandidate(probe, EvidenceTier.PROBE, priority=0.1),
            AllocationCandidate(winner, EvidenceTier.SCALE, priority=10.0),
        ],
        total_units=100.0,
    )
    by_id = {a.entity_id: a.units for a in allocations}

    assert by_id[probe] == pytest.approx(20.0)
    assert by_id[winner] == pytest.approx(80.0)


def test_allocator_never_allocates_to_killed_hypothesis() -> None:
    dead = uuid4()
    live = uuid4()
    allocations = AllocationPolicy().allocate(
        [
            AllocationCandidate(dead, EvidenceTier.KILLED, priority=1000.0),
            AllocationCandidate(live, EvidenceTier.PROBE, priority=1.0),
        ],
        total_units=10.0,
    )

    assert {a.entity_id for a in allocations} == {live}


def test_allocator_respects_candidate_cap_when_possible() -> None:
    ids = [uuid4() for _ in range(3)]
    allocations = AllocationPolicy(
        exploration_fraction=0.0,
        max_candidate_fraction=0.50,
    ).allocate(
        [
            AllocationCandidate(ids[0], EvidenceTier.SCALE, priority=100.0),
            AllocationCandidate(ids[1], EvidenceTier.PILOT, priority=1.0),
            AllocationCandidate(ids[2], EvidenceTier.PILOT, priority=1.0),
        ],
        total_units=100.0,
    )
    by_id = {a.entity_id: a.units for a in allocations}

    assert by_id[ids[0]] <= 50.0 + 1e-9
    assert sum(by_id.values()) == pytest.approx(100.0)
