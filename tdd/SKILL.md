---
name: tdd
description: "Use test-driven development with a strict public-interface testing style. Apply red-green-refactor one behavior at a time while enforcing Sandi Metz's 2x3 grid: incoming queries, incoming commands, and outgoing command expectations only. Use when writing, reviewing, or refactoring tests for object-oriented code; do not test private methods, outgoing queries, or indirect side-effects. Applies to Python/pytest and similar OO test suites."
---

# TDD

## Philosophy

Use red-green-refactor to grow behavior one small step at a time.

Keep the current testing scope strict:

- Test through the public interface.
- Prefer the smallest useful example that proves one behavior.
- Do not default to integration-style tests.
- Do not test implementation details.
- Let the 2x3 grid decide whether a test belongs.

The goal is not "more tests." The goal is a small set of tests that describe the public contract and survive refactors.

## The 2x3 Grid (Allowed Cells Only)

| Message Origin | Query (ask -> return value) | Command (tell -> side effect) |
|---------------|-----------------------------|--------------------------------|
| Incoming      | Assert return value         | Assert public observable state |
| Self          | -                           | -                              |
| Outgoing      | -                           | Expect message sent (args)     |

Delete any test that does not fit one of the three allowed cells.

## Rules (Non-Negotiable)

- Write one test at a time.
- Write only enough production code to pass the current test.
- Refactor only when the suite is green.
- Never test private methods or their results.
- Never assert return value of outgoing queries.
- Never test distant or indirect side-effects; only assert the correct command was sent.
- Mock only outgoing commands (never incoming or self).
- Use real objects for incoming messages.
- Optimize for the smallest set of tests that prove the public contract survives refactor.

## Workflow

1. Confirm the SUT and the public interface you are trying to grow or protect.
2. List behaviors, not implementation steps.
3. Pick the thinnest vertical slice that proves the path works.
4. Write one failing test for one behavior.
5. Check that the test fits an allowed cell in the grid.
6. Write the minimum production code to make that test pass.
7. Refactor while staying inside the public contract.
8. Repeat one behavior at a time.

## Red-Green-Refactor

### 1. Red

Write a single failing test for the next behavior.

- The test must describe observable behavior.
- The test must use the public interface.
- The test must fit one allowed grid cell.
- If it does not fit, rewrite it or delete it.

### 2. Green

Write the minimum code needed to pass that test.

- Do not anticipate later tests.
- Do not add speculative abstractions.
- Keep the implementation narrow until the next failing test justifies more.

### 3. Refactor

Once green, improve the code and tests without changing behavior.

- Remove duplication.
- Clarify names.
- Push complexity behind small public interfaces.
- Re-run tests after each refactor step.

Never refactor while red.

## Vertical Slices, Not Horizontal Batches

Do not write a large batch of tests up front and then a large batch of implementation.

Use tracer bullets:

```text
RED   -> one failing test for one behavior
GREEN -> minimal code to pass
REFACTOR -> improve design while green
REPEAT
```

This keeps the tests coupled to real behavior instead of imagined structure.

## Decision Checklist

- Check whether the test calls a method on the SUT; if yes treat as incoming -> keep (query or command).
- Check whether the test asserts something the SUT returns; if yes keep as incoming query.
- Check whether the test asserts state a caller can observe; if yes keep as incoming command.
- Check whether the test expects a message sent to another object; if yes keep as outgoing command (mocked).
- Otherwise delete.

## Per-Cycle Checklist

- Does this test describe behavior rather than implementation?
- Does it touch only the public interface?
- Does it fit one of the three allowed grid cells?
- Is it the smallest test that proves the next behavior?
- Did I write only enough code to pass?
- Am I refactoring only after reaching green?

## Python / pytest-mock Patterns

```python
# Incoming query
def test_diameter():
    wheel = Wheel(rim=26, tire=1.5)
    assert wheel.diameter == pytest.approx(29.0)

# Incoming command -> public state change
def test_ratio_after_cog_change():
    gear = Gear(chainring=52, cog=11)
    gear.set_cog(10)
    assert gear.ratio == pytest.approx(5.2)

# Outgoing command -> message sent
def test_notifies_observer_on_cog_change(mocker):
    observer = mocker.Mock()
    gear = Gear(chainring=52, cog=11, observer=observer)

    gear.set_cog(10)

    observer.changed.assert_called_once_with(cog=10, chainring=52)
```

## Delete These Patterns

- Spying or asserting on private methods.
- Asserting return values from collaborator queries.
- Asserting deep or indirect state changes.
- Mocking incoming messages or self.

Use this skill as a strict filter: every proposed test must match one allowed cell or be deleted.
