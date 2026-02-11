---
name: skill-oo
description: Guidance for writing object-oriented code from scratch in Python or Ruby. Use when asked how to model domains, define responsibilities, design collaborations, or structure new OO code for clarity, testability, and change resilience.
---

# Object-Oriented Code Writing

## Overview
Write new code as small, intention-revealing objects that collaborate through stable messages. Favor clear responsibilities, explicit roles, and simple object graphs over flags and control-heavy logic.

## Quick start
- State the domain goal in one sentence.
- Identify the main collaborators and their responsibilities.
- Name each role with a noun that reflects intent (Invoice, Plan, Policy).
- Define the minimal message each role must answer.
- Keep orchestration thin: prefer message sending over branching.
- Add tests at the role level before wiring integrations.

## When to avoid or delay
- Keep a simple procedure when the work is tiny and unlikely to change.
- Avoid abstract base classes or frameworks until you see repetition.
- Do not introduce factories unless construction logic is already branching.

## Workflow
1. Capture the domain story.
   - Write a short narrative of the behavior in the user's language.
   - Extract the nouns (roles) and verbs (messages).
2. Assign responsibilities.
   - Each class should do one kind of thing well.
   - Move data+behavior together; avoid "god" objects.
3. Design the collaboration.
   - Sketch who sends which message to whom.
   - Prefer composition to inheritance unless behavior truly varies.
4. Define object APIs.
   - Keep methods small and intention-revealing.
   - Favor query/command separation where practical.
5. Handle variation.
   - If behavior changes by type, use polymorphic role players.
   - If selection varies by input, centralize it in a factory.
6. Test the roles.
   - Unit-test each role with focused inputs.
   - Keep integration tests thin and behavior-oriented.

## Writing guidelines
- Prefer nouns for classes, verbs for methods.
- Use explicit domain terms, not technical placeholders.
- Keep objects small; split once a class owns multiple reasons to change.
- Make dependencies explicit via constructor injection.
- Avoid flag arguments; prefer different role objects.

## Language notes
### Python
- Prefer plain classes with `__init__` and small methods; avoid premature ABCs.
- Use `@dataclass` only when the class is truly data-heavy and behavior-light.
- Keep module boundaries clear; treat modules as namespaces for related roles.
- Favor explicit dependencies over globals; pass collaborators in constructors.
- Test with pytest and focus on behavior, not implementation details.

### Ruby
- Favor small POROs; avoid callbacks and metaprogramming until needed.
- Use modules for shared behavior, not as a default inheritance substitute.
- Keep `initialize` lightweight; move setup logic into collaborators.
- Prefer keyword arguments for clarity in constructors.
- Test with RSpec or Minitest and keep specs intention-revealing.

## Output expectations
- Provide a proposed object model: roles, responsibilities, messages.
- Offer a collaboration outline (who calls what, in what order).
- Suggest test cases aligned to each role.
- Provide a small starter scaffold when asked for code.

## Example prompts
- "How should I model a checkout flow with coupons?"
- "Design OO classes for a notification system."
- "What objects and messages fit this domain story?"
