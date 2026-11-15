"""Tests for MemoryRouter: footprint-based payload routing."""

import pytest

from memoryrouter import MemoryRouter, memory_footprint


def test_footprint_grows_with_payload():
    small = memory_footprint([1, 2, 3])
    large = memory_footprint([1, 2, 3] * 100)
    assert large > small


def test_footprint_handles_nesting_and_cycles():
    nested = {"a": [1, [2, 3]]}
    assert memory_footprint(nested) > 0
    cycle = []
    cycle.append(cycle)
    assert memory_footprint(cycle) > 0


def test_expert_rejects_oversized_payload():
    from memoryrouter import MemoryExpert
    expert = MemoryExpert("small", 100)
    with pytest.raises(ValueError):
        expert.handle([0] * 1000)


def test_route_picks_cheapest_fitting_expert():
    router = MemoryRouter()
    router.add_expert("tiny", 64, cost=1.0)
    router.add_expert("huge", 1_000_000, cost=5.0)
    payload = [0] * 50
    assert router.route(payload).name == "huge"


def test_route_prefers_smallest_sufficient_budget_on_tie():
    router = MemoryRouter()
    router.add_expert("big", 10_000, cost=1.0)
    router.add_expert("bigger", 100_000, cost=1.0)
    assert router.route([1, 2, 3]).name == "big"


def test_route_no_fit_raises():
    router = MemoryRouter()
    router.add_expert("tiny", 8)
    with pytest.raises(ValueError):
        router.route([0] * 500)


def test_route_and_handle_and_report():
    router = MemoryRouter()
    router.add_expert("e", 10_000)
    out = router.route_and_handle([1, 2, 3])
    assert "stored by e" in out
    report = router.memory_report()
    assert report["e"] > 0
