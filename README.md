# MemoryRouter

[![CI](https://github.com/kapildhinwa2010-dev/MemoryRouter/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/MemoryRouter/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/MemoryRouter/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/MemoryRouter/actions/workflows/codeql.yml)

Route payloads to experts by memory footprint: big payloads land on big budgets.

## What it does

Each expert declares a byte budget. The payload is measured with a recursive
size estimate (containers included) and routed to the cheapest expert whose
budget fits, breaking ties by the smaller budget.

    from memoryrouter import MemoryRouter

    router = MemoryRouter()
    router.add_expert("cache", 1024, cost=1.0)
    router.add_expert("store", 1048576, cost=5.0)
    print(router.route_and_handle([0] * 100))

## API

- memory_footprint(payload) - recursive size estimate in bytes
- MemoryExpert(name, budget_bytes, cost) - one routing target
- MemoryRouter.add_expert / route / route_and_handle / memory_report

## Honest results and limitations

- The footprint estimate is approximate: sys.getsizeof walks containers but
  undercounts shared or interned objects, and does not descend into arbitrary
  objects or numpy buffers.
- Budgets are declared, not enforced by the allocator; "stored" means counted,
  not persisted.
- No eviction or overflow handling: an over-budget payload is rejected.

## Status

Part of the kapildhinwa2010-dev toolkit experiments. CI and CodeQL run on
every push to main. License: MIT.
