# Project Instructions character cap example

This deliberately repetitive brief tests whether customization can remove generic and repeated context while keeping confirmed behavior and constraints.

## Project brief

We are building a small appointment system for a neighborhood clinic. The front desk team needs to see appointments and manage bookings during calls, and the clinic administrator needs to configure which clinicians work on which days. Patient information is private and must not be used to train AI models. Receptionists manage bookings; administrators configure schedules. Please keep those roles distinct. We already have an application and want to improve it rather than replace it. The current code may not reflect every approved requirement, so follow the repository instructions and approved product specification when they disagree. Do not send patient notifications or make production data changes without explicit approval. We want concise instructions that help chats work across planning and implementation without repeating the full specification.

## Paste-ready result

```markdown
# Clinic project

Follow the repository instructions and approved product specification; treat code as evidence of current behavior, not approval of intent. Keep receptionist booking access separate from administrator schedule configuration. Protect patient information and never use it to train AI models. Preserve the existing application and its conventions. Do not send patient notifications or change production data without explicit approval.
```

The result preserves the source-of-truth rule, confirmed roles, privacy constraint, existing-application context, and approval boundary while removing repeated background. Its paste-ready content is **448 characters** (Markdown included; the surrounding code fence excluded). Count with the language's character length, not bytes or tokens.
