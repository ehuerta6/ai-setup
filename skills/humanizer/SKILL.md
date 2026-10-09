---
name: humanizer
description: Rewrite prose so it sounds natural, specific, and appropriate for its actual writer and audience while preserving facts, meaning, and intent.
---

# Humanizer

Rewrite text so it reads like deliberate human writing rather than generic model output.

Preserve what the text actually says.

Do not invent facts, claims, metrics, quotes, citations, dates, or decisions.

## Process

### 1. Identify the voice

Use, in order:

1. explicit tone instructions;
2. writing samples from the user;
3. surrounding project or document style;
4. the natural register of the artifact.

Technical documentation should remain technical.

A casual message should remain casual.

Do not force every artifact into the same voice.

### 2. Preserve the information

Before rewriting, identify:

- factual claims;
- names;
- numbers;
- dates;
- technical terminology;
- citations;
- qualifications;
- uncertainty;
- decisions.

These must survive unless the user explicitly asks to remove them.

### 3. Remove artificial writing patterns

Look for patterns such as:

- staged openers before the actual point;
- unnecessary "not X, but Y" contrasts;
- conclusions that merely repeat the paragraph;
- forced groups of three;
- repetitive sentence openings;
- excessive em dashes or decorative punctuation;
- vague claims of importance;
- generic corporate or marketing language;
- inflated significance;
- unnecessary hedging;
- filler;
- chatbot phrases;
- excessive bolding or decorative formatting;
- abstract language where a concrete statement exists.

Do not remove a pattern mechanically when it genuinely fits the writer's voice or the meaning.

### 4. Rewrite structurally

Do not patch suspicious phrases one by one.

Rewrite the sentence or paragraph around its actual point.

Prefer:

- concrete statements;
- natural sentence-length variation;
- specific verbs;
- appropriate repetition of established terminology;
- direct transitions;
- language the intended reader would actually expect.

### 5. Validate

Compare the rewrite against the source.

Check that you did not accidentally:

- add a claim;
- remove a constraint;
- change a number;
- strengthen uncertainty into certainty;
- weaken a technical distinction;
- replace established terminology;
- change the writer's actual opinion.

## Artifact handling

When editing technical files, preserve:

- code blocks;
- inline code;
- commands;
- paths;
- URLs;
- identifiers;
- YAML or other metadata;
- data structures.

Only rewrite prose unless explicitly asked otherwise.

## Rules

- Meaning before style.
- Specificity before flourish.
- Preserve the writer's real voice when evidence of it exists.
- Do not make text artificially casual to make it "human."
- Do not introduce slang, humor, opinions, or personality that are not supported by context.
- Do not fabricate supporting detail to make a sentence sound better.
- Natural writing can still be formal, technical, concise, or repetitive when the subject requires it.

## Completion

A rewrite is complete when:

- every important fact is preserved;
- the intended tone still fits;
- obvious model-writing patterns are removed;
- the prose reads naturally at paragraph level;
- no unsupported information was introduced.
