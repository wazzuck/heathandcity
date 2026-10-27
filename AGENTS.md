# Guidelines for AI Coding Agents

> A portable, project-agnostic rule set for AI coding sessions.
> Copy this file into the root of a repository as `AGENTS.md`; most
> agent harnesses load it automatically in every session.
> Keep the rules here generic, and record project facts in `docs/` or
> in a short local section at the end of this file.
> Status: binding. Derived from the `finance_dreams` rule set and
> generalised for reuse across projects.

---

## 1. Purpose and scope

1. This repository is developed collaboratively across several
   machines, sessions and agents, with Git as the only synchronisation
   channel.
2. More than one agent may be active at the same time, and the `main`
   branch can advance while an agent works.
3. The repository, not the chat, is the memory: a fresh session reads
   the committed state instead of re-deriving the project.
4. The rules below exist to do two things: keep work recoverable, and
   stop one agent from silently overwriting another agent's work.
5. Where a project document conflicts with this file, stop and ask the
   operator which one wins. Do not choose silently.

---

## 2. Start Here (every session)

Before reading or editing anything, do the following in order.

1. Read this file (`AGENTS.md`) fully.
2. Read the project documents that exist, in this order:
   `docs/technical/AI_WORKFLOW.md`, `docs/ARCHITECTURE.md`, `STATUS.md`,
   `docs/PRODUCT_STRATEGY_AND_GUARDRAILS.md`, and
   `docs/CHANGE_PLAYBOOK.md` when the task is a schema, protocol or
   decoder change. Skip a document that does not exist; do not invent
   it.
3. Check `git status` for uncommitted or untracked work.
4. If the tree is clean, run `git pull` to take the latest `main`.
5. If the tree is not clean, stop and ask whose work it is before
   pulling, editing or committing.
6. Run `git worktree list` to see task branches another agent has
   checked out.
7. If `scripts/install_hooks.sh` exists, run it once per clone so the
   guards run before every commit.
8. Open only the module, report or file the task actually needs.

Target: productive within a handful of short documents.

Open the first reply with a bootstrap line, so the operator can see what
was read and what task was understood, for example:

    Bootstrap: AGENTS + AI_WORKFLOW + ARCHITECTURE + STATUS read;
    task = <task>.

---

## 3. Protecting existing work (binding, read this twice)

Never overwrite code you did not write. Git protects committed history
only; two uncommitted edits to one file can still lose one of them.

1. Pull before you read, and read before you edit.
2. Re-read the exact file immediately before editing it. A file is only
   as fresh as the last read: another agent, machine or tool may have
   changed it since.
3. Prefer a targeted edit over a full-file rewrite. A targeted edit
   fails loudly when the file has moved on; a full write silently
   discards the other change.
4. If a targeted edit does not match, do not force it. Re-read the
   file, understand the difference, then decide.
5. Check `git status` and `git log` for the files you are about to
   touch. If a file already has changes you did not make, stop and ask.
6. Never delete, move or rename a file you did not create unless the
   task explicitly asks for it.
7. Never rewrite, reformat or "clean up" unrelated code in the same
   change. Keep the diff limited to the task.
8. One file, one writer at a time. If two agents must share a checkout,
   give them disjoint file sets and pull immediately before editing and
   committing.
9. Commit in small, coherent steps with a message that says why the
   change exists.
10. After editing, inspect the diff. Confirm that only the intended
    lines changed, and that no unrelated file was touched.
11. Merge finished branches one at a time. Do not merge two branches
    that touch the same files without resolving them deliberately.
12. Never force-push a shared branch, and never discard another
    person's commit to make a check pass.
13. When a merge conflicts, re-read both sides and combine their intent.
    Do not pick one side blindly.
14. When in doubt, stop and ask. A paused session is cheap; lost work
    is not.

---

## 4. Mandatory policies for coding agents

1. **Pull before changing anything.**
   - At the start of a session, fetch and integrate the latest `main`.
   - Do this only on a clean tree, or after the operator has resolved
     any local changes.
   - Re-pull before committing if the session has been long or the
     repository is shared.

2. **Commit every change.**
   - Every code, test, configuration or documentation change ends in a
     commit.
   - Do not leave changes unstaged or uncommitted when a task ends.
   - Commit related changes together; do not mix unrelated work.

3. **Push after committing, and merge finished work.**
   - Push each commit so the other machines can see it.
   - A task branch is not finished until it is merged into `main` and
     pushed.
   - On a solo project, merge locally; do not open a pull request and
     do not leave a finished branch stranded.
   - Never leave a commit unpushed at the end of a task.

4. **Run a legal and patent check on every new feature.**
   - Check that the feature does not break the law or infringe another
     party's patent or licence.
   - If a risk exists, state it in bold red text, stop making changes,
     and wait for the operator to decide.
   - Record the decision in the repository, not only in chat.

5. **Keep the dependency manifest current.**
   - When a library or tool is added, record it in the project manifest
     in the same change: `requirements.txt`, `package.json`,
     `Cargo.toml`, `go.mod`, `pyproject.toml` or the equivalent.
   - Record non-package system dependencies too, with a short note on
     who needs them and why.
   - A fresh clone must be reproducible from the manifest.

6. **Keep documentation within 80 columns.**
   - Markdown, design documents, code comments and docstrings wrap at
     a maximum of 80 characters, ideally 76 to 80.
   - Tables and ASCII diagrams fit within 80 columns, preferably 75 to
     78.
   - The only exception is a standalone link that cannot be broken.
   - Wide lines force horizontal scrolling in terminals and on mobile
     screens; do not create them.

7. **Explain multi-step work step by step.**
   - Start with a one-line summary.
   - Then use a numbered list, one idea per step.
   - Do not bury a procedure in a long sentence.
   - Apply this to documents, chat replies and commit messages.

8. **Bootstrap the session explicitly.**
   - Follow "Start Here" before doing anything else.
   - Open the first reply with the bootstrap line.
   - Read every document named as binding, every session.
   - Do not re-derive the project from scratch.

9. **Extend, do not fork.**
   - Extend the existing modules, interfaces and conventions.
   - Never build a parallel parser, differ, generator, client or
     service alongside the existing one.
   - If a new module is genuinely required, state why in the commit
     message.
   - Generated artefacts are never hand-edited; change the generator,
     then regenerate.

10. **Keep project state current.**
    - If the project keeps a `STATUS.md`, treat it as owned by `main`
      and update it during close-out, not on a task branch.
    - Move finished items to Done, keep Next short, and record open
      decisions under Blocked.
    - If an interface changed, update `docs/ARCHITECTURE.md` and any
      change playbook in the same task.
    - A stale status file is a defect: the next session will act on it.

11. **Isolate parallel work.**
    - One agent, one git worktree, one branch per task:
      `git worktree add ../<project>-<task> -b task/<task>`.
    - If the project provides helper scripts such as
      `scripts/new_worktree.sh <task>`, use them.
    - Assume `origin/main` will advance while you work; sync before
      finishing.
    - Parallel tasks are safe only when they touch disjoint files.
    - Never run two tasks against the same module.
    - Prefer the project's close-out script, for example
      `scripts/finish_task.sh --status "..."`; otherwise perform the
      same order by hand: sync, test, merge, push, remove the worktree.

12. **Expand acronyms on first use.**
    - Write the words out, then the acronym in brackets, for example
      "Continuous Integration (CI)". Later uses may be the acronym
      alone.
    - Scope covers chat replies, documentation, code comments, commit
      messages and pull-request text.
    - Each chat reply is a fresh document; expand again every time.
    - Must expand: domain vocabulary and anything a senior engineer
      outside the project's field would not know.
    - May stand bare: widely understood computing, finance and business
      terms, such as API, CLI, CPU, RAM, OS, IDE, HTML, XML, JSON, CSV,
      URL, PDF, ID, AI and QA.
    - When in doubt, expand. Prefer the reader's comprehension.
    - Code identifiers, type names, symbols, file extensions and CLI
      flags are used verbatim and are not expanded.
    - If a checker exists, it runs in the commit gate and in
      Continuous Integration (CI); a bare first use fails the build.

13. **Document every step of the code.**
    - Embedded documentation is part of the code, not an optional
      extra. The explanation lives at the point of the step, never only
      in a chat log or commit message that will drift away from it.
    - Write for a reader who knows neither this codebase, nor the
      language's idioms, nor the business domain. Assume a top-to-bottom
      read.
    - Give each file a header: what it is for, what it is deliberately
      not for, and the invariants it relies on.
    - For every function, method, class, struct and dataclass, describe
      its purpose, every argument (meaning, units, ranges), its return
      value, what it raises or reports, and any side effect.
    - Add a narrative walkthrough: follow the code in execution order,
      and say what each statement or small group of statements does and
      why. Number the steps so a reader can say "step 4" and be
      understood.
    - Explain effect and intent together; a mechanical reading of the
      syntax is not enough.
    - Where a step depends on a domain fact, state that fact.
    - Explain every constant, table, limit and magic number: what it
      means, what its value is, and who consumes it.
    - Expect the documentation to rival the code in volume. If a reader
      cannot follow a step, the file is not finished.
    - Wrap comments and docstrings at 80 columns, and expand acronyms.
    - Keep comments true. When the code changes, update or delete the
      comment in the same commit. A stale comment is a defect.
    - Document a generated artefact through its generator, never by
      hand: write the explanation in the generator, then regenerate.
    - Scope covers new and edited source, scripts, tools and tests,
      including shell and any other language in the tree.

14. **Verify before handing over.**
    - Run the tests, the linters and the guard scripts the project
      provides.
    - If a check fails, fix the cause; do not disable the check.
    - Do not claim a task is done because the code "looks right".
    - Report skipped checks and the reason, rather than hiding them.

15. **Use British English for customer-facing text and documentation.**
    - All language that is facing the customer, user or client, and all
      repository documentation, comments and docstrings must use British
      English conventions (for example: "summarisation", "prioritisation",
      "categorisation", "customisation", "synchronise", "dialogue",
      "colour", "behaviour", "licence" for noun, "practice" for noun,
      "modelling", "centre", "programme").
    - Code identifiers, external library Application Programming
      Interface (API) names, protocol constants or JSON keys specified by
      external standards remain verbatim.
    - When drafting or editing Graphical User Interface (GUI) copy,
      prompts, reports, documentation or commit messages, standardise on
      British English spelling and idioms.

---

## 5. Definition of done

A task is done only when all of these are true.

1. The requested change is implemented, and nothing unrelated changed.
2. The test suite and the guard scripts pass, or every skip is
   explained.
3. Documentation and code comments match the code.
4. `STATUS.md`, if present, is updated during close-out.
5. The work is committed, pushed and merged into `main`.
6. The task worktree and branch are removed or clearly closed.
7. The final reply states what changed, what was verified, and what
   remains open.

---

## 6. Anti-patterns

Do not do these.

1. "While I am here" refactors that widen the diff.
2. Inventing a new implementation beside the existing one.
3. Hand-editing generated files.
4. Silent interface changes.
5. Regenerating everything when one file changed.
6. Answering from memory instead of re-reading the repository.
7. Editing from an earlier read instead of re-reading the file.
8. Committing unrelated files because they happened to be in the tree.
9. Rewriting or deleting another agent's work to make a check pass.
10. Force-pushing a shared branch.
11. Opening a pull request for a solo task and leaving the branch
    unmerged.
12. Claiming success without running the checks.

---

## 7. Adapting this file to a project

Keep the rules generic in this file, and put project facts elsewhere.

1. Keep section 3 unchanged: it is the core protection against
   overwritten work.
2. Add the project's architecture, workflow and strategy to `docs/`,
   and reference them from section 2 instead of expanding this file.
3. Replace example paths and directory names with the real ones in
   section 4, policies 9, 11 and 13.
4. Name the languages, build tools, test command and guard scripts
   once, in a short "Project facts" note at the end.
5. Remove or tighten a policy only when the project cannot enforce it;
   say so in the same change.
6. Record machine-specific details (hostnames, paths, credentials)
   locally, never in the shared file.
7. Review this file when the workflow changes, and commit the change.

---

## 8. Provenance

This file generalises the rule set used in the `finance_dreams`
repository: git synchronisation across standalone machines, worktree
isolation, re-read-before-edit discipline, commit and push on every
change, 80-column documentation, expanded acronyms, step-by-step
explanations, and step-by-step embedded code documentation.

The exchange-specific policies from that repository are deliberately
absent. Add project-specific rules only where they apply.
