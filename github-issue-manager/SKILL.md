---
name: github-issue-manager
description: Manage GitHub issues in the current repo via gh CLI. Use when asked to look up, inspect, design/plan, create, or implement a specific GitHub issue; or to update issue title/body/labels/state with explicit confirmation.
---

# GitHub Issue Manager

## Overview

Use gh CLI to safely read and update issues in the current repo with explicit confirmation for any modifications.

## Core Rules

- Always use `gh` CLI against the current repo for all issue operations and lookups.
- Never change an issue (title/body/labels/state/close/reopen) without explicit user confirmation and showing the exact diff first.
- When given a real name (first/last), resolve the GitHub username yourself using `gh` (for example `gh api /search/users?q="Full Name"`), then confirm the match if ambiguous.
- If scope, acceptance criteria, or priority are unclear, ask pointed questions before changing or creating anything.
- Enforce title and body constraints.
- Title: 1 line, fewer than 60 characters.
- Body: 1 paragraph, maximal density, no fluff.

## Workflow

1. Identify the target issue by number or search with `gh issue list --search`.
2. Read the current issue details with `gh issue view` and capture title/body/labels/state.
3. If the request is unclear, ask focused questions about scope, acceptance, or priority.
4. Draft the proposed update or new issue content that meets title/body constraints.
5. Show the exact diff against current title/body/labels/state before applying changes.
6. Ask for explicit confirmation.
7. Apply changes with `gh issue edit` or create with `gh issue create` once confirmed.
8. Report what changed and link to the issue.

## Diff Format

Show exact diffs using the current values fetched from `gh issue view` and the proposed replacements. Prefer a small, unified diff block that includes title, body, labels, and state as applicable.
