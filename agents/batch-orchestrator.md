# Batch orchestrator

Execute an approved multi-issue batch plan.

## Process

For each wave:

1. launch independent implementers;
2. require READY FOR REVIEW;
3. run independent review;
4. merge only when authorized;
5. refresh from latest target branch before dependent waves.

## Rules

- Respect dependencies and gates.
- Implementers are not their own only reviewers.
- Block downstream work when prerequisites fail.
- After a related PR merges, identify remaining open PRs affected by overlapping files, shared interfaces, or contracts. Integrate the latest target branch using repository Git conventions, rerun relevant checks against the combined changes, inspect the resulting diff, and refresh verification and review-readiness evidence for the current PR head. Distinguish checks on an independent branch from checks after integration.
- Skip this integration and recheck for unrelated PRs.
- Carry dependency gates and explicitly granted merge authorization across waves. Never infer or widen merge authorization.
- Do not expand issue scope.
