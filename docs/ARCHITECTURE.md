# Architecture and extension plan

## Implemented prototype

Synthetic source + structured draft → evidence validation → dependency validation → priority and blocker analysis → JSON plan + Markdown report + follow-up draft.

The extraction prompt is provided for manual use with an AI assistant; there is no model integration. Local file reads and report writes are the only I/O. No external service is connected. Approval remains blocked for external actions, irrespective of an input `approved` field.

## Design decisions

- Standard library only: the prototype can be inspected and run without installing dependencies.
- An explicit `as_of` date makes urgency scoring reproducible.
- Exact source quotations make unsupported text detectable but do not prove semantic accuracy.
- Dependency sorting and urgency ranking are separate outputs.
- Dependencies block tasks until a future trusted completion system verifies them. This version does not accept completion assertions.
- No executable shell commands or external tool calls are derived from meeting content.

## Future phases — not implemented

1. **Model adapter:** choose a provider, validate structured output, handle retries and cost limits. Treat model output as untrusted.
2. **Reviewer interface:** display source and proposed action together, allow correction, and record reviewer identity and timestamps.
3. **Private workflow storage:** store revisions, completion events, and approval receipts outside the public repository.
4. **Sandbox connectors:** test task-system and email adapters on fictional accounts, with dry-run previews and idempotency keys.
5. **Controlled execution:** scope each approval to the exact action payload, invalidate it on edits, and use least-privilege credentials.
6. **Evaluation:** measure evidence support, owner/date accuracy, false decisions, and reviewer correction rate before live use.

No service prices, efficiency claims, or production results are asserted by this demo.
