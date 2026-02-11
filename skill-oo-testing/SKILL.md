---
name: skill-oo-testing
description: "Enforce Sandi Metz 2x3 grid testing for object-oriented code. Use when writing, reviewing, or refactoring tests to keep only public-interface coverage: incoming queries/commands and outgoing command expectations. Delete tests that touch private methods, outgoing queries, or indirect side-effects. Applies to Python/pytest and similar OO test suites."
---

# Sandi Metz Grid Testing

## Overview

Apply the 2x3 grid to keep only public-interface tests and delete everything else. Focus on minimal tests that preserve the public contract across refactors.

## The 2x3 Grid (Allowed Cells Only)

| Message Origin | Query (ask -> return value) | Command (tell -> side effect) |
|---------------|-----------------------------|--------------------------------|
| Incoming      | Assert return value         | Assert public observable state |
| Self          | -                           | -                              |
| Outgoing      | -                           | Expect message sent (args)     |

Delete any test that does not fit one of the three allowed cells.

## Rules (Non-Negotiable)

- Never test private methods or their results.
- Never assert return value of outgoing queries.
- Never test distant or indirect side-effects; only assert the correct command was sent.
- Mock only outgoing commands (never incoming or self).
- Use real objects for incoming messages.
- Optimize for the smallest set of tests that prove the public contract survives refactor.

## Workflow

1. Identify the SUT and its public interface.
2. Classify each test into the grid.
3. Keep only tests that map to allowed cells.
4. Rewrite borderline tests to target public state or outgoing commands.
5. Delete everything else.

## Decision Checklist

- Check whether the test calls a method on the SUT; if yes treat as incoming -> keep (query or command).
- Check whether the test asserts something the SUT returns; if yes keep as incoming query.
- Check whether the test asserts state a caller can observe; if yes keep as incoming command.
- Check whether the test expects a message sent to another object; if yes keep as outgoing command (mocked).
- Otherwise delete.

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
