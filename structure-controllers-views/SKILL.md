---
name: structure-controllers-views
description: Structure Rails controllers and views so HTTP entrypoints stay thin, orchestration lives in objects, templates render a single page/view model, and branching moves out of actions and views. Use when reviewing, refactoring, or generating Rails controller actions, presenters, page objects, partial-selection objects, or ERB templates that currently contain conditionals, multiple instance variables, or mixed domain and rendering logic.
---

# Structure Rails Controllers and Views

## Overview

Treat controllers as thin adapters. Move orchestration into objects, build one page/view model for rendering, and replace template branching with polymorphism or preselected partials.

## Core Rules

- Keep each action focused on HTTP concerns: read input, call one collaborator, return a response.
- Avoid conditionals in actions when they choose business or presentation behavior. Push that branching into a use case object, result object, or listener callback flow.
- Avoid scattered `render` or `return` branches in the entrypoint. Prefer one delegated call plus explicit success/failure callbacks or one final response decision.
- Pass one root object to the view, such as `@page`, `page`, or `view_model`.
- Avoid multiple unrelated instance variables or template locals. Compose them into a page object instead.
- Avoid conditionals in templates. Decide what to render before the template runs, then let the template ask the page object which partial, section, or component to render.
- When rendering differs by role or state, choose a different page/presenter object instead of putting `if/else` inside one object.
- Do not let templates query repositories, inspect framework objects, or make domain decisions.

## Refactor Workflow

1. Identify the mixed responsibilities in the current action.
2. Extract the use case into an object that receives collaborators explicitly.
3. Choose a response pattern:
   - Use listener callbacks when the controller must translate success and failure into HTTP responses.
   - Use a result object when the framework style favors returning one response object.
   - Use a page/view model when assembling render data for a template.
4. Collapse view state into one root page object.
5. Replace template conditionals with polymorphic page objects, role objects, or preselected partial/template names.
6. Verify the final entrypoint mostly reads as: parse, delegate, render/return.

## Preferred Patterns

### Use Case + Listener

- Use for endpoint actions that can succeed or fail in different ways.
- Let the controller or handler implement `*_success` and `*_failed` callbacks.
- Keep framework response code at the edge; keep domain decisions in the use case.

### Page / View Model

- Use when a template needs multiple pieces of data or rendering choices.
- Expose intention-revealing messages such as `header_partial`, `title`, `summary`, or `actions`.
- Make the template consume the page object instead of separate primitives.
- If behavior differs by role or state, instantiate a different page object per variant.

### Role / Variant Objects

- Use when rendering differs by role, status, feature flag, or resource subtype.
- Prefer multiple objects answering the same message over branching in the caller or template.
- Keep variant selection in a factory or use case, not in the template and not buried inside one conditional-heavy presenter.

## Review Heuristics

- Flag actions that fetch records, branch on state, and render inline.
- Flag templates with `if/else` blocks that choose layout or navigation by role or state.
- Flag controllers that assign several unrelated instance variables for one page.
- Prefer one extracted object with a small public interface over many helper methods on the controller or template.

## Expected Output

- Name the objects to introduce or keep.
- State the single responsibility of each object.
- Show the messages passed between the entrypoint, use case, and page object.
- Produce the refactor in Rails style instead of generic pseudocode.

## Resources

- Read `references/rails.md` for Rails controller, listener, page object, and partial patterns.
