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
- Before implementing, make sure the code is in good form to build on. Refactor first if that helps implement the task.
- Prefer local verification such as a CLI scaffold, unit tests, or functional tests.
- Test locally. Do not expect the user to test it for you.
- Ask the user about assumptions unless you are absolutely sure.
- Favor OOP in the Alan Kay sense.
- When the code is working, thoroughly review the change and look for ways to reduce complexity.

## Workflow

1. Figure out the test strategy before editing code.
2. Split the task into smaller steps if the full change would be large.
3. Refactor the current code first if that gives you a better place to implement the task.
4. Make the smallest complete change.
5. Run the relevant local test, scaffold, or functional flow.
6. Review the finished code and simplify it.

## Expected Output

- State the test plan before implementation.
- State the subtask split if the change should be broken down.
- State any assumptions that need user confirmation.
- Implement the smallest complete step.
- Report what you ran locally.
- Report any simplifications made after the code was working.
