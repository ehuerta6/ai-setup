# Skills

Reusable workflows and capabilities for AI-assisted development.

Each skill has one clear responsibility. Its detailed behavior lives in its own `SKILL.md`.

## Planning

| Skill | Use when |
| --- | --- |
| `grill-me` | A feature, plan, or decision still has ambiguity |
| `to-spec` | Decisions need to become a durable specification |
| `to-issues` | A spec or large feature needs to become connected GitHub Issues |

## Implementation and review

| Skill | Use when |
| --- | --- |
| `implement-issue` | Implementing one approved GitHub Issue |
| `verify-change` | Running and reporting the repository's actual checks |
| `review-pr` | Reviewing implementation against requirements and engineering standards |
| `debug-with-evidence` | Diagnosing bugs through reproduction and tested hypotheses |
| `github-flow` | Working with commits, issues, PRs, and GitHub conventions |
| `firebase` | Working with Firebase Auth, Firestore, Security Rules, Emulator Suite, Functions, and related services |

## Agent workflow

| Skill | Use when |
| --- | --- |
| `handoff` | Passing unfinished work to a fresh agent or session |
| `retro` | Improving the AI workflow based on completed work |
| `writing-for-agents` | Writing or maintaining instructions consumed by agents |

## Writing and design

| Skill | Use when |
| --- | --- |
| `humanizer` | Removing AI-writing patterns while preserving meaning and facts |
| `unslop` | Auditing and cleaning technical writing |
| `impeccable` | Designing, reviewing, or improving frontend UI and UX |

## Career

| Skill | Use when |
| --- | --- |
| `resume-review` | Reviewing, roasting, rewriting, or tailoring a technical resume |

## Typical flow

```text
Idea
 ↓
grill-me
 ↓
to-spec
 ↓
to-issues
 ↓
implement-issue
 ↓
verify-change
 ↓
review-pr
```
