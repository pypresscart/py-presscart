---
name: no-claude-coauthor
description: Commit messages in this repo must NEVER include a Co-Authored-By trailer referencing Claude, Anthropic, or any AI assistant.
applies_to: git commits, amends, PR descriptions
---

# Rule: No Claude co-author trailer

## The rule

When creating a git commit in this repo, the message **must not** contain any
`Co-Authored-By:` trailer that attributes authorship to Claude, Anthropic, an
AI assistant, or any model identifier (e.g. `Co-Authored-By: Claude <...>`,
`Co-Authored-By: Claude Opus ...`, `Co-Authored-By: Claude Code <...>`).

Human co-author trailers are fine. Machine co-author trailers are not.

## Why

The maintainer wants git history to attribute commits to the human author who
is accountable for the change. AI-assistance attribution belongs in the PR
description, not in the permanent commit log.

## How to apply

- When using `git commit` with a HEREDOC message, **omit** the Claude
  co-author line entirely. Do not replace it with a different AI attribution.
- When amending, strip any pre-existing Claude co-author trailer rather than
  preserving it.
- If a default template in this environment appends such a trailer, override
  it explicitly.
- This applies regardless of whether the user asks "with co-authored" —
  politely decline the AI attribution and commit without it.
