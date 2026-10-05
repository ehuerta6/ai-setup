# Agents

Specialized roles used when isolating responsibility or context improves the work.

| Agent | Purpose |
| --- | --- |
| `pr-reviewer` | Independently review completed work before merge |
| `mentor` | Guide implementation while explaining important engineering concepts |
| `supabase-database-reviewer` | Review Supabase, PostgreSQL, migrations, RLS, and database security |
| `batch-orchestrator` | Coordinate multi-issue execution waves and review gates | `issue-batch-orchestrator`, `review-pr`, `github-flow` |

Agents should remain reusable. Project-specific product behavior stays in the project repository.
