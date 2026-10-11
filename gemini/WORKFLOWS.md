# Optional Gemini workflows

These recipes route work to Google products when their strengths fit, then return to canonical `ai-setup` skills for evaluation. They are optional and do not create new repository workflows.

Product references and availability were checked against the [official Google source links](README.md#source-currency) on **October 10, 2026**. Re-check changing access, quotas, and privacy terms before use.

## Technical research

**Use when:** the question depends on current external information and a source-grounded comparison.

1. Use Gemini Deep Research to discover current sources. Review its plan and retain links to the original sources.
2. Put selected, permitted source documents in Gemini Notebook (formerly NotebookLM) and ask focused questions that point back to the source passages.
3. Use [`research-and-compare`](../skills/research-and-compare/SKILL.md) to compare options against explicit criteria and make the recommendation.

**Output:** a concise decision with primary sources, tradeoffs, uncertainties, and next evidence needed. **Verify:** open primary sources; model-generated summaries and citations are discovery aids, not primary evidence. Deep Research limits and Workspace-connected sources depend on account and settings. **Do not use when:** the issue is already answered by authoritative local/project context or the material is not approved for external services.

## Independent PR review experiment

**Use when:** you want to see whether a second coding agent finds useful issues on a bounded change.

1. Have one agent implement the change and record requirements, diff, and checks.
2. In Antigravity, provide the issue and diff, then invoke the canonical [`review-pr`](../skills/review-pr/SKILL.md) guidance. Keep the review independent until findings are recorded.
3. Compare actionable findings, false positives, missed requirements, elapsed effort, cost/access, and duplicated work.

**Output:** a short comparison and any verified actionable findings. **Verify:** check each finding against source and acceptance criteria; route final decisions through the normal repository workflow. Antigravity compatibility is untested until the procedure above is executed. **Do not use when:** the change is trivial, external review would expose restricted code, or two reviews add no material confidence. This is not a required merge gate.

## UI and prototype exploration

**Use when:** a visual concept or fast disposable model can resolve a concrete UI question.

1. State the design question and alternatives. Optionally use AI Studio Build or Nano Banana to sketch disposable concepts.
2. Recreate the chosen interaction in a local disposable prototype using [`prototype`](../skills/prototype/SKILL.md), when a working experiment is needed.
3. Evaluate hierarchy, real states, accessibility, responsiveness, and the rendered interface with [`impeccable`](../skills/impeccable/SKILL.md).

**Output:** a recorded decision, tested prototype, and limitations. **Verify:** generated pictures do not demonstrate functioning controls, keyboard use, responsive layout, or accessible contrast. Treat generated code as untrusted and inspect it before reuse. **Do not use when:** a written decision resolves the question faster or the visual model is likely to bias the production design without evidence.

## Documentation and course learning

**Use when:** you have an approved, bounded source set to study or explain.

1. Add authoritative documents or course materials you are allowed to process to a Gemini Notebook (formerly NotebookLM) notebook.
2. Ask for a structured synthesis, glossary, source-linked questions, or study output. Keep the questions tied to specific sources.
3. For a continuing learning workspace, use the existing [course-companion](../project-instructions/course-companion.md) or [research-workspace](../project-instructions/research-workspace.md) Project Instruction as relevant.

**Output:** a source-grounded study aid with references to materials to recheck. **Verify:** follow citations back to original passages; identify gaps in the supplied sources. **Do not use when:** no trustworthy sources are available or the materials contain information you cannot upload.

## Creative images and video

**Use when:** exploratory media helps explain an idea, storyboard a demo, or collect visual feedback.

1. Use Nano Banana/image generation for visual variants, or Flow/Veo for a short rough explainer or storyboard clip.
2. Label generated media as exploratory; collect feedback on the concept.
3. For product UI, validate against a working prototype and [`impeccable`](../skills/impeccable/SKILL.md). For written claims, check the source material independently.

**Output:** a clearly labeled draft image or video and a record of intended use. **Verify:** inspect factual details, rights/consent, artifacts, and current export/access constraints. These tools do not create editable design source or production-ready deliverables by themselves. **Do not use when:** the media would imply unverified product behavior, includes sensitive uploads, or a simple diagram or text explanation is clearer.

## Workspace and Gems

**Use when:** work already belongs in a connected Google app, or a repeat conversational task benefits from saved instructions.

1. Use Gemini in Workspace for a bounded task on information you are authorized to access, such as summarizing a Drive document or drafting a Calendar event.
2. Consider a Gem for a repeated Gemini Apps task. Keep its instruction set small and review any uploaded knowledge files.
3. Use canonical repo skills for engineering tasks. If a Gem is useful, manually adapt a small instruction summary; do not assume it syncs with or replaces `SKILL.md`.

**Output:** an in-app result or saved Gem with a clear owner and purpose. **Verify:** inspect generated or edited content and check Connected Apps, activity settings, admin policy, and sharing/access boundaries. Entitlements vary by account, language, region, and Workspace configuration; Google AI consumer plan benefits and Gemini API billing are separate. **Do not use when:** the action needs repository-aware changes, an auditable engineering workflow, or access to personal/confidential data has not been approved.
