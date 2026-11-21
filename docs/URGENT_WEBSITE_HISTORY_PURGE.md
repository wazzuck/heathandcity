# URGENT: Website History Purge Awaiting Approval

**Status: URGENT — not yet executed.** Blocked on the explicit
operator approval that `AGENTS.md` policy 18 requires before any
shared history is rewritten. Last updated: 21 November 2026.

## Why this matters

The public repository `wazzuck/heathandcity` has a clean working
tree, but its 179-commit history still serves personal data to
anyone who reads an old commit:

1. Two files removed on 17 November 2026 that carried
   special-category data under the United Kingdom (UK) General
   Data Protection Regulation (UK GDPR): a founder background file
   (a health diagnosis affecting a child and the operator,
   relatives' employment and religion, redundancy, savings and
   assets) and a local consulting strategy (family details and
   health-dependent planning notes).
2. The former `practice-vault/` subtree: test fixtures naming real
   correspondents, mock practice records, and the master passphrase
   written as a literal.
3. The operator's e-mail address in every author and committer
   identity across the history.

Deliberately left in place: the Corringham Court business postal
address, because it is the published data-controller address of the
live privacy policy, the JSON-LD block and `llms.txt`.

## Prepared artefacts (outside every repository)

- `/home/neville/backups/replace_text_website.txt` — 155 tested
  replacement rules with mode 600 permissions. This is the same set
  that scrubbed the `datavault` repository, minus the three
  business-address rules.
- `/home/neville/backups/heathandcity-pre-southgate-purge-20261117.git`
  — the pre-Southgate mirror. Take a fresh mirror before this purge
  as well.

## Execution steps (only after operator approval)

1. Step 1: take a fresh mirror of the repository into
   `/home/neville/backups/`.
2. Step 2: run `git filter-repo --force` with `--replace-text` and
   `--replace-message` pointing at `replace_text_website.txt`, plus
   an `--email-callback` that rewrites the author and committer
   e-mail to the neutral `neville@example.com`.
3. Step 3: verify with a whitespace-normalised sweep over every
   object, every commit message and every identity, and confirm the
   current tree is byte-identical apart from the deliberately
   retained address.
4. Step 4: force-push `main` and any other branch.
5. Step 5: open a GitHub Support request for unreachable-object and
   cache purging, quoting the repository, the force-push date and
   the pre-purge commit identifiers. Merge this note's execution
   record into `STATUS.md` item 1 in the same change.
6. Step 6: delete the fresh mirror only after GitHub confirms the
   purge.

## Related open item

`STATUS.md` item 1 under "Next" records the earlier Southgate
purge, which still needs its own GitHub Support request for the old
commit identifiers `d81ec67`, `dc2dbd6`, `cb530ac` and `52d0b5e`.

## Approval

Policy 18 states: "Do not attempt the rewrite without explicit
operator approval." Reply with approval to proceed.
