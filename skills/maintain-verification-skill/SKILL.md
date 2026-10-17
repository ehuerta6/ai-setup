---
name: maintain-verification-skill
description: Keep a project's verification skill and feature map accurate through source inspection and live exercise without concealing product regressions.
---

# Maintain verification skill

Use when application routes, commands, authentication, environment, selectors, or user behavior changed enough that a **project-local** `verify-*` skill could be stale. Update only that skill's owned files, not product code.

Adapted from [PStack's maintain-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-verification-skill/SKILL.md) for Codex and project-specific Git workflows.

## Locate and index

Find the project's intended local verification skill, normally under `.agents/skills/` for Codex or its configured host directory. If absent, use `create-verification-skill`. If more than one candidate fits, determine the target rather than mixing them.

Check its `features/README.md` index against feature documents. Correct missing, obsolete, duplicate, and dead entries without generating an unnecessary inventory.

## Check source, feature by feature

Read the implementation, entry points, relevant tests and permissions for **every mapped feature**. Look for source-supported user journeys missing from the map. Record precise source paths for suspected drift.

Read-only subagents may independently analyze features in parallel if the host supports them. They must not drive the app or edit files. Do not treat an unverified subagent summary as proof of behavior.

Reconcile findings as map drift, harness drift, real product regression, or unresolved until exercised.

## Drive each mapped feature

Exercise **every** mapped feature at least once using the project's own launch, doctor, drive, evidence, and cleanup instructions. Combine journeys to save time when safe, but record each feature's actual result.

- Use one controlled driver per shared long-running instance; isolate fresh CLI/TUI sessions as documented.
- Doctor before the first drive, on new sessions when required, and after surprises. Reset or relaunch a stuck app instead of assuming a healthy process means healthy state.
- Collect proof of the action, visible result, and relevant side effect. Check evidence persists through cleanup and keep credentials out.
- Clean up temporary state after failures and at final teardown; stop only owned processes.
- Re-drive a fixed harness before claiming it is repaired.
- When a feature cannot be reached, report the attempted route and concrete missing prerequisite, never mark it passed.

Use safe test fixtures; do not migrate production data into agent environments by default.

## Correct drift without hiding defects

Repair only the verification skill's instructions, feature map, and owned helper scripts, using the repository's Git conventions. If an app feature itself is broken, report a product defect separately; do not edit the app, change expected behavior to match a regression, or weaken assertions to pass.

## Report the outcome

Choose one outcome:

- **clean:** complete source and live coverage, nothing to change, no empty PR.
- **changed:** one focused PR or repository-approved delivery of proven verification-skill corrections; include affected re-run evidence.
- **blocked:** explain why complete source/live coverage or safe delivery was not possible.

Report revision, environment, feature coverage, evidence locations, unreachable cases, and product defects. A partial pass is not `clean`.
