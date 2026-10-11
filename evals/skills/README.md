# Skill evaluations

Run the deterministic fixture checks with:

```sh
python3 scripts/validate_catalog.py
```

`cases.json` records positive and routing-away examples for `grill-me`,
`implement-issue`, and `review-pr`, plus observable instruction anchors. The
catalog validator checks fixture shape, skill references, route-example
coverage, and that each behavior anchor remains in its canonical skill.

These checks are structural. The prompts and expected routes are hand-authored
routing examples, not executions of Codex or Claude discovery and not evidence
that an agent would choose the expected skill or behave as described. To compare
a skill change, run the same catalog command on the baseline and candidate
revisions, then compare its result and inspect any changed instruction anchors.
When a suitable agent runtime is available, run the prompts manually against
both revisions and record actual selections and outputs separately; model calls
are optional and are not required in CI.
