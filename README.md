# MemoryRouter

MemoryRouter is a small Python library that estimates the memory footprint of a payload and selects a registered `MemoryExpert` whose declared byte budget can accommodate that estimate. It is an early-stage utility (version 0.1.0), not a storage engine or memory-management system.

## What is implemented

- `memory_footprint(payload)` estimates bytes using `sys.getsizeof`. It recursively visits dictionary keys and values and items in lists, tuples, sets, and frozensets, while tracking object identities to avoid revisiting cycles and shared references.
- `MemoryExpert(name, budget_bytes, cost=1.0)` represents a named target with a positive byte budget and non-negative cost. Its `handle(payload)` checks the estimated size against its budget and, if it fits, updates `bytes_served` and `calls` and returns a descriptive string.
- `MemoryRouter.add_expert(...)` registers experts. `route(payload)` selects a fitting expert by lowest declared cost, breaking cost ties with the smaller budget. `route_and_handle(payload)` routes and calls the selected expert's handler. `memory_report()` returns a mapping of expert names to their accumulated `bytes_served` estimates.

## Install

From a checkout of this repository, install the project and its declared runtime dependency with:

```sh
python -m pip install .
```

The project metadata requires Python 3.9 or newer and declares `numpy>=1.24` as a dependency. The implementation currently uses only the Python standard library; NumPy is not used by the routing code.

## Example

```python
from memoryrouter import MemoryRouter

router = MemoryRouter()
router.add_expert("small", budget_bytes=1_000, cost=1.0)
router.add_expert("large", budget_bytes=100_000, cost=2.0)

payload = {"values": list(range(100))}
expert = router.route(payload)
print(expert.name)

result = router.route_and_handle(payload)
print(result)
print(router.memory_report())
```

`route()` only returns the selected expert; it does not update accounting. `route_and_handle()` invokes `handle()`, which increments the selected expert's `bytes_served` and `calls` counters when the estimated footprint fits. These counters describe estimates and calls, not persisted or allocated storage.

## Estimation and scope

The footprint is an approximate Python object-size estimate, not a measurement of total process or payload memory. Recursive traversal is limited to the built-in container types listed above. Other objects are counted only by their `sys.getsizeof` result; for example, the backing data buffer of a NumPy array is not recursively measured. Shared or interned objects may also make the result differ from a payload's actual memory use.

Budgets and costs are user-declared selection inputs. The library does not enforce allocator limits, transfer payloads, persist data, evict items, or provide overflow handling beyond raising `ValueError` when no expert fits. A selected expert's handler returns a status string; it does not store the payload. This release does not provide a command-line interface, external expert integrations, or performance benchmarks.

## Tests and CI

The repository test suite was run on the checked-out commit with:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider
```

Result: **7 passed**. The GitHub Actions CI workflow is configured to run pytest, compile the module and tests, and perform an import smoke test on Python 3.10, 3.11, and 3.12. This README reports the local test run; it does not assert a remote CI run status.

## License

The repository includes an MIT License. See [LICENSE](LICENSE) for the license text and copyright notice.
