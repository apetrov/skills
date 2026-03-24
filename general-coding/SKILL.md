---
name: general-coding
description: Implement code changes in small, low-risk, testable steps. Use when writing, refactoring, or reviewing production code and the task benefits from atomic commits, change sets under roughly 250 lines, explicit test planning before edits, local verification, assumption-checking with the user, and post-change simplification. Especially useful when a task feels broad and should first be broken into smaller subtasks.
---

# General Coding

## Overview

Keep changes small, testable, and easy to review. Figure out how to test the task first, make atomic changes, ask about assumptions when unsure, and simplify the code after it works.

## Rules

- Avoid large changes.
- Make sure changes are atomic.
- Avoid changes longer than 250 LOC. Break the task into subtasks first when needed.
- Before working on the task, figure out how you are going to test it.
- Do not guess at performance bottlenecks. Only optimize after proving where time is spent.
- Measure before tuning for speed, and only optimize when one part clearly dominates.
- Prefer simple algorithms until measurement shows input size or workload justifies something fancier.
- Prefer simple algorithms and simple data structures because they are usually less buggy and easier to implement.
- Let data shape the design. Choose and organize data structures well so the code stays obvious.
- Before implementing, make sure the code is in good form to build on. Refactor first if that helps implement the task.
- Prefer local verification such as a CLI scaffold, unit tests, or functional tests.
- Test locally. Do not expect the user to test it for you.
- Ask the user about assumptions unless you are absolutely sure.
- Favor OOP in the Alan Kay sense.
- Avoid type annotations unless they are clearly necessary for a boundary, tool, or correctness constraint.
- Prefer duck typing and message-oriented design over prematurely pinning collaborators to explicit types.
- When the code is working, thoroughly review the change and look for ways to reduce complexity.

## Naming

- Name classes by responsibility or stable domain role, not storage shape, framework detail, or vague status words.
- Name methods by the message they answer in the domain; prefer intention-revealing names over implementation-shaped names.
- Name variables after the concrete domain thing they represent; if a name needs comments to explain an encoding, redesign the data shape.
- Name roles from the caller's point of view: either the message the collaborator must answer or the purpose it serves in the conversation.
- Prefer specific role names like `Preparer`, `Wheel`, `Parts`, or purpose names like `ForPaying`; be suspicious of `Manager`, `Helper`, `Processor`, `Service`, `Handler`, `data`, `info`, and `value`.
- For boundary interfaces such as ports, name them by purpose using a `ForX` pattern when it fits; let adapters append the technology detail later.
- During review and refactoring, treat naming as design work: if a name is generic, it is probably hiding an unclear responsibility.

## Workflow

1. Figure out the test strategy before editing code.
2. Check whether the task has a performance angle; if so, decide how to measure it before changing code.
3. Split the task into smaller steps if the full change would be large.
4. Refactor the current code first if that gives you a better place to implement the task.
5. Make the smallest complete change.
6. Run the relevant local test, scaffold, or functional flow.
7. Review the finished code and simplify it, including replacing unnecessary cleverness with simpler data structures or logic.

## Expected Output

- State the test plan before implementation.
- State the subtask split if the change should be broken down.
- State any assumptions that need user confirmation.
- Implement the smallest complete step.
- Report what you ran locally.
- Report any measurement approach used for performance-sensitive work.
- Report any simplifications made after the code was working.
