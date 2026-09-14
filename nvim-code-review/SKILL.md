---
name: nvim-code-review
description: "Prepare Git changes for review in a running Neovim instance through nvim-mcp, using side-by-side diffs, ordinary buffers for new files, and REVIEW: notes."
---

# Neovim Code Review

Prepare Neovim for the user's review. Do not review, edit code, or add `REVIEW:` notes unless asked.

## Determine the review set

Use the repository containing Neovim's working directory and respect any explicit base or file scope. Review the current change, not the entire dirty tree. Determine scope in this order:

1. Use the paths, feature, issue, or PR named by the user.
2. Otherwise infer scope from the task and editor context, grouping files from the same feature or package. Treat unrelated top-level untracked directories as separate changes.
3. If multiple scopes remain and choosing could include unrelated files, ask before replacing the layout.

Use Git to find changed files within that scope. Open relevant source, tests, configuration, migrations, and documentation. Omit generated, binary, and visual assets unless requested or central to the change. Omit incidental metadata.

When no base is specified:

- Compare scoped local changes with `HEAD` and include untracked files.
- For a branch or PR, use the merge base with its unambiguous target or upstream; otherwise ask for the base.

Collect paths with Git's NUL-delimited output. Track both paths for copies and renames, and include deletions.

## Prepare Neovim

1. Connect through `nvim-mcp` and inspect editor state. Stop if Neovim's working directory is outside the repository.
2. Check `modified_buffers` before closing anything. If present, ask the user to save them or authorize discarding them.
3. Close existing windows and listed buffers with editor commands, without writing files.
4. Create one tab per reviewed file:
   - Modified or renamed file: base version on the left, current working-tree file on the right, with both windows in diff mode.
   - Added or untracked file: current file in one ordinary, non-diff window.
   - Deleted file: base version on the left and an empty current-side scratch buffer on the right, in diff mode.
5. Keep base and synthetic buffers read-only, unmodifiable, unswappable, clearly named, and assigned a suitable filetype when practical.
6. Finish on the first current-side file and verify tabs, windows, and diff modes. If nothing changed, leave a clean editor and tell the user.

Read base content from Git objects; never overwrite working-tree files or store snapshots in the repository. Prefer Neovim scratch buffers. Put unavoidable snapshots in a dedicated system temporary directory and report it.

Treat revisions, paths, and buffer names as quoted data. Prefer structured Lua or argument arrays. If a file fails, report it and the remaining layout.

## Review notes

Preserve `REVIEW:` comments in current-side buffers. Do not add, change, remove, resolve, or save them unless asked.

When asked to process notes, find `REVIEW:` in reviewed current-side files, read their context, and return a file-and-line summary. Treat text after the marker as an instruction. Implement or remove notes only when explicitly asked; ignore base-side scratch buffers.
