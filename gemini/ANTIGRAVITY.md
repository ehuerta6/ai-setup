# Antigravity compatibility and adoption

Antigravity is Google's coding-agent surface. This guide describes documented compatibility, not a successful local integration test. `gemini/` contains human-read documentation; it is **not** an auto-loaded skill directory.

## CLI setup

If you choose Antigravity CLI, follow Google's current [installation and authentication instructions](https://www.antigravity.google/docs/cli/install/) for your operating system and account. The documented binary is `agy`; after setup, check it with `agy --version`, then launch `agy` from the project directory. The first run may require Google account sign-in. The supported install methods and authentication options can change, so review the official page before running its commands. This guide does not install the CLI or require a paid plan.

## Gemini CLI transition

Google announced that Antigravity CLI is its successor for consumer coding-agent workflows. Its May 19, 2026 transition notice says Gemini CLI and Gemini Code Assist IDE extensions stop serving Google AI Pro, Ultra, and individual free users on June 18, 2026; enterprise licensing and Gemini API-key access to Gemini CLI are described separately. Check the [transition notice](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) and [migration guide](https://www.antigravity.google/docs/cli/gcli-migration/) for your account before following older Gemini CLI setup instructions. Gemini CLI and Antigravity CLI are distinct products despite some migration compatibility.

## Documented instruction and skill locations

The current [Antigravity rules documentation](https://www.antigravity.google/docs/rules-workflows?tab=ide) describes `AGENTS.md` and `GEMINI.md` as recognized instruction files. Workspace rules can be placed at the workspace root or in subdirectories; the agent walks upward from the edited file and loads applicable files, with more specific directory rules taking precedence. It also supports `.agents/rules/*.md` (and legacy `.agent/rules/*.md`) files. Global paths vary by surface:

| Surface | Global instruction files | Modular global rules |
| --- | --- | --- |
| Antigravity 2.0 / IDE | `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md` | `~/.gemini/config/rules/*.md` |
| Antigravity CLI | `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md` | `~/.gemini/config/rules/*.md` and `~/.gemini/antigravity-cli/rules/*.md` |

Consult the docs for surface-specific syntax and precedence details.

The [Agent Skills documentation](https://www.antigravity.google/docs/skills?tab=ide) lists these discovery paths:

| Surface | Workspace skill | Global skill |
| --- | --- | --- |
| Antigravity 2.0 | `<workspace-root>/.agents/skills/<skill-folder>/SKILL.md` | `~/.gemini/config/skills/<skill-folder>/SKILL.md` |
| Antigravity CLI | `<workspace-root>/.agents/skills/<skill-folder>/SKILL.md` | `~/.gemini/antigravity-cli/skills/<skill-folder>/SKILL.md` |
| Antigravity IDE | `<workspace-root>/.agents/skills/<skill-folder>/SKILL.md` | `~/.gemini/config/skills/<skill-folder>/SKILL.md` |

Across the listed surfaces, `.agents/skills` is the current workspace default; older `.agent/skills` remains supported. Keep workspace skills under version control when they are meant to be shared with that project.

Antigravity reads skill metadata for discovery and loads the full instructions when relevant or invoked. Google documents a folder containing `SKILL.md` with YAML frontmatter; this matches the broad structure of this catalog's skills. That structural match does not establish that every instruction or tool call behaves identically across agents. Antigravity 2.0, CLI, and IDE may differ; verify on the version and surface you intend to use.

## Adopt selected canonical skills

Use `ai-config-builder` in its **Adopt** mode to inspect the target project's instructions, classify relevant artifacts, and select only what fits. `adopt` is a skill mode, not a shell command. Keep canonical copies in this `ai-setup` repository; adoption means deliberately copying selected files into the consuming project, where project-specific instructions can take precedence.

For example, after choosing `research-and-compare` and `review-pr`, create a workspace skill directory and copy just those skill folders:

```sh
mkdir -p /path/to/project/.agents/skills
cp -R /path/to/ai-setup/skills/research-and-compare /path/to/project/.agents/skills/
cp -R /path/to/ai-setup/skills/review-pr /path/to/project/.agents/skills/
```

Replace both paths with real local paths. Read the target project's instructions first, review the copied material, and keep changes project-specific. If you need global discovery instead, copy selected folders to the surface-specific path above: `~/.gemini/config/skills/` for Antigravity 2.0 or IDE, or `~/.gemini/antigravity-cli/skills/` for CLI. Global skills are available across workspaces on that machine. Do not copy all of `ai-setup` by default.

Do not create a `GEMINI.md` that simply duplicates `AGENTS.md`. Antigravity documents both names; add a focused adapter only when a real, reproducible incompatibility requires one. Do not move canonical files into this `gemini/` directory.

## Compatibility test plan

This is a proposed test, **not executed** in this environment. No `agy` or Antigravity IDE executable was available during documentation work. The documentation task required no sign-in or paid access; the optional compatibility test requires an Antigravity surface you already have access to and may require sign-in under that surface's normal authentication flow. It does not require a paid plan or destructive experiment. Run it only in a disposable or non-critical project:

1. Record the surface and version (`agy --version` for CLI), and make a temporary project with a minimal `AGENTS.md` containing a harmless, observable instruction such as “For this compatibility check, prefix your final response with `AGENTS-loaded:`.”
2. Copy canonical `research-and-compare` and `review-pr` skill folders into `.agents/skills/` using the example above. Confirm the agent can discover or explicitly invoke each by name.
3. Ask it to use `research-and-compare` to compare two supplied local text notes only; request a recommendation that distinguishes evidence from assumptions. Then ask it to use `review-pr` on a tiny, local sample diff or fixture and report requirement findings separately from engineering findings. Do not use a real repository or external data for this test.
4. Inspect the outputs for the marker, skill-specific process, citation/tool expectations, and any unsupported claims. Compare with the canonical skill instructions and record missed steps, extra prompting, surface differences, and any privacy or approval prompts.
5. Report the version, exact setup, observations, limitations, and anything not run. A skill appearing in discovery is not proof it was followed correctly; inspect behavior. Remove the temporary fixture when finished.

Until this check has actually been run, compatibility is **documented structural support; behavioral interoperability not tested**. Do not treat this guide as evidence that Antigravity executed these skills successfully.

## Official sources reviewed October 10, 2026

- [Antigravity Agent Skills](https://www.antigravity.google/docs/skills?tab=ide) — paths, metadata, and discovery.
- [Antigravity rules](https://www.antigravity.google/docs/rules-workflows?tab=ide) — instruction file names, scope, and precedence.
- [Gemini CLI transition announcement](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) — consumer and enterprise transition context.
- [Antigravity CLI migration](https://www.antigravity.google/docs/cli/gcli-migration/) — migration details.
- [Antigravity CLI installation and authentication](https://www.antigravity.google/docs/cli/install/) — current install and authentication options; review before use.

Documentation can change after this review date; re-check before setup or making compatibility claims.
