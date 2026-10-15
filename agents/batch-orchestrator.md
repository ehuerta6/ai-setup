# Batch orchestrator

Execute an approved multi-issue batch plan. This coordination guidance is **TESTING**; validate it in real workflows before adopting it as a default.

## Process

For each wave:

1. Confirm issue scope, dependencies, shared files/contracts, and whether parallel work is useful and supported. Assign each worker a distinct issue and ownership. Use separate branches/worktrees when supported and useful; otherwise serialize work. See `skills/issue-flow/SKILL.md` for planning guidance.
2. Track meaningful worker states: `QUEUED`, `RUNNING`, `BLOCKED`, `READY FOR REVIEW`, `CHANGES REQUESTED`, `VERIFIED`, `READY FOR OWNER`, `COMPLETED`. Do not create status documents for simple tasks. For a batch handoff, report issue/task, scope, branch/worktree, status, current head SHA and PR when applicable, verification evidence, review outcome, blocker, and next action.
3. Coordinate from observable runtime events when the host exposes them (worker state changes, review, required checks, blockers, merges, stale branches, or human decisions). Otherwise use explicit checkpoints, such as worker handoff, review completion, CI completion, and post-merge integration. Markdown cannot subscribe to events or keep workers running; do not require continuous polling or fabricate events/messages.
4. Require independent review for every completed work item in an approved multi-issue batch, consistent with the gate in `templates/BATCH.md`; implementers are not their own only reviewers. Skip it only when the applicable repository workflow or approved batch plan explicitly authorizes that exception. Omission from the plan is not authorization. Route actionable in-scope findings to the responsible worker when the runtime permits it. Use `skills/review-pr/SKILL.md`; a green CI result does not establish requirements review.
5. Before `READY FOR OWNER`, inspect the actual PR requirements and diff, resolve review findings, and verify required checks and relevant tests against the current PR head SHA. Report gaps and checks that were skipped, pending, or unavailable. This state means ready for the owner's decision, never permission to merge.
6. Refresh affected dependent PRs after a related merge as described below.

## Recovery and gates

- A worker may continue technical actions already within the approved issue: run relevant checks, inspect logs, fix an in-scope defect, request review, refresh an affected branch, and update evidence.
- Before recovery, use a correction budget explicitly set by the applicable repository workflow or approved batch plan; if neither sets one, declare a task-appropriate bounded budget before retrying. Do not silently increase it. Stop when it is exhausted, or earlier when another attempt is unlikely to produce useful evidence. If unresolved, report the evidence and next decision needed.
- Report blockers as implementation failure, verification failure, unavailable environment, external authorization, or pending human decision. Stop or escalate instead of retrying without a useful next step.
- Ask the owner before resolving ambiguous requirements, changing approved architecture/security boundaries, expanding scope, destructive or irreversible operations, production data/permissions, production deployment, or merging, unless that exact action was previously authorized.
- Never infer approval from green CI, reviewer approval, worker completion, validation success, or authorization granted for another PR. Respect project-specific permissions and repository workflow.
- Block dependent work when a prerequisite fails. Do not invent requirements.

## Dependent PR integration

After a related PR merges, identify remaining open PRs affected by overlapping files, shared interfaces, or contracts. Integrate the latest target branch using repository Git conventions, inspect for duplicate or reintroduced changes, review the effective diff, rerun relevant checks against the combined changes, and refresh review-readiness evidence for the current PR head. Distinguish checks on an independent branch from checks after integration. Skip integration and rechecks for unrelated PRs.

Carry dependency gates and explicitly granted merge authorization across waves without widening it.
