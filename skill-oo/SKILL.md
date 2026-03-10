---
name: skill-oo
description: Guidance for writing object-oriented code from scratch in Python or Ruby. Use when asked how to model domains, define responsibilities, design collaborations, or structure new OO code for clarity, testability, and change resilience.
---

# Object-Oriented Code Writing

## Overview
Write new code as small, intention-revealing objects that collaborate through stable messages. Favor clear responsibilities, explicit roles, and simple object graphs over flags, conditionals, and control-heavy logic.

## What objects should be
- Anthropomorphic: treat each object as having a job; describe it in terms of what it is responsible for doing.
- Polymorphic: let different objects answer the same message when behavior varies; avoid branching on type in callers.
- Role-playing: model collaborators as roles in a conversation, each with a narrow responsibility in the domain.
- Loosely-coupled: depend on stable messages, not concrete classes or internal state.
- Factory-created: centralize object selection and assembly when construction varies, so callers stay focused on behavior.
- Message-sending: prefer asking objects to do work over pulling data out and making decisions elsewhere.
- Anti-conditional: avoid conditionals that select behavior in callers; prefer role objects or polymorphic message receivers when behavior varies.

## Non-negotiable rules
- Start concrete; do not abstract early.
- Prefer composition over inheritance.
- Avoid conditionals that choose behavior in callers.
- Do not expose data for other objects to interpret.
- Give each object one clear responsibility.
- Depend on messages, not concrete classes.
- Keep constructors simple; do not put domain work in them.
- Prefer domain names for classes and verb phrases for messages.
- Introduce factories only when object selection or assembly already varies.
- Keep code easy to test through the public interface.

## Nil / Null values
- Never return `None` / `nil` as a domain value.
- If an object may be missing, return a null object that conforms to the same public interface.
- Make the null object explicit and intention-revealing in the domain language.
- Callers should send the same messages to the null object as to the real object, without extra branching.

## Exceptions
- If you believe breaking the nil / null rule is necessary, stop and ask for permission before doing it.

## Language notes
### Python
- Prefer plain classes with `__init__` and small methods; avoid premature ABCs.
- Use `@dataclass` only when the class is truly data-heavy and behavior-light.
- Favor explicit dependencies over globals; pass collaborators in constructors.
- Test with pytest and focus on behavior, not implementation details.

### Ruby
- Favor small POROs; avoid callbacks and metaprogramming until needed.
- Use modules for shared behavior, not as a default inheritance substitute.
- Keep `initialize` lightweight; move setup logic into collaborators.
- Prefer keyword arguments for clarity in constructors.
- Test with RSpec or Minitest and keep specs intention-revealing.

## Required output
- List the proposed objects and the single responsibility of each.
- List the public messages each object should answer.
- Describe the collaboration flow: who sends which message to whom.
- Suggest tests for public behavior only: incoming queries, incoming commands, and outgoing commands.
