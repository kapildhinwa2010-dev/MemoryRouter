# MemoryRouter - Route payloads to experts by memory footprint
# Part of the Kapildhinwa2010-dev Toolkit.

"""MemoryRouter - footprint-based payload routing.

Lineage: DNA_DYNIMO routers. Each expert has a memory budget. The payload
is measured with a conservative recursive size estimate and routed to the
cheapest expert whose budget fits, so big payloads land on big experts.

The estimate is approximate: it walks containers with sys.getsizeof and
undercounts shared or interned objects. See README limitations.
"""

from __future__ import annotations

import sys

__all__ = ["memory_footprint", "MemoryExpert", "MemoryRouter"]


def memory_footprint(payload) -> int:
    """Conservative recursive size estimate in bytes (containers included)."""
    seen = set()

    def size(obj) -> int:
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        total = sys.getsizeof(obj)
        if isinstance(obj, dict):
            for key, value in obj.items():
                total += size(key) + size(value)
        elif isinstance(obj, (list, tuple, set, frozenset)):
            for item in obj:
                total += size(item)
        return total

    return size(payload)


class MemoryExpert:
    """A routing target with a byte budget and a served-bytes counter."""

    def __init__(self, name: str, budget_bytes: int, cost: float = 1.0) -> None:
        if not name:
            raise ValueError("name must be non-empty")
        if budget_bytes <= 0:
            raise ValueError("budget_bytes must be > 0")
        if cost < 0:
            raise ValueError("cost must be >= 0")
        self.name = name
        self.budget_bytes = int(budget_bytes)
        self.cost = float(cost)
        self.bytes_served = 0
        self.calls = 0

    def handle(self, payload) -> str:
        footprint = memory_footprint(payload)
        if footprint > self.budget_bytes:
            raise ValueError("payload of {} bytes exceeds budget of {} bytes".format(footprint, self.budget_bytes))
        self.bytes_served += footprint
        self.calls += 1
        return "stored by {} ({} bytes)".format(self.name, footprint)


class MemoryRouter:
    """Route each payload to the cheapest expert whose budget fits it."""

    def __init__(self) -> None:
        self.experts: list = []

    def add_expert(self, name: str, budget_bytes: int, cost: float = 1.0) -> None:
        self.experts.append(MemoryExpert(name, budget_bytes, cost))

    def route(self, payload) -> MemoryExpert:
        if not self.experts:
            raise ValueError("no experts registered")
        footprint = memory_footprint(payload)
        fitting = [e for e in self.experts if e.budget_bytes >= footprint]
        if not fitting:
            raise ValueError("no expert budget fits {} bytes".format(footprint))
        return min(fitting, key=lambda e: (e.cost, e.budget_bytes))

    def route_and_handle(self, payload) -> str:
        return self.route(payload).handle(payload)

    def memory_report(self) -> dict:
        return {e.name: e.bytes_served for e in self.experts}
