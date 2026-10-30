# Social Close · AI Workflow Starter Kit

**Turn meeting notes into an evidence-backed, human-reviewed action plan.**

This portfolio prototype demonstrates human judgment supported by AI: structured extraction, source verification, dependency planning, prioritization, and approval gates. It is a working local Python project, not a connected production automation.

All people, organizations, dates, and situations in the examples are synthetic. No private client materials are included.

## Additional project: LinkedIn Multi-Content Studio

[Open the LinkedIn project](linkedin-content-studio/README.md) · [Read the generated demo pack](linkedin-content-studio/examples/expected/content_pack.md)

Build seven draft formats from a vetted fictional brief: insight, contrarian, checklist, carousel outline, video script, poll, and newsletter draft. Includes source tracking, repetition review, a two-week editorial CSV, and seven additional tests. Offline template prototype; no AI API or publishing integration.

## Quick start

Requires Python 3.10+; no third-party packages, API keys, or network access required.

```bash
PYTHONPATH=src python -m socialclose_workflows.engine examples/meeting.json --out output
PYTHONPATH=src python -m unittest discover -s tests -v
```

Open `output/review.md` for the review report and follow-up draft. `output/plan.json` contains machine-readable results. A generated reference is in `examples/expected/`.

## Workflow

1. A person prepares synthetic meeting notes with stable source IDs.
2. An AI assistant can propose structured JSON using `prompts/extract.md`. The included example already contains that structured draft, so the demo works offline.
3. The Python engine checks the JSON and exact evidence quotations.
4. It validates dependencies, produces an ordered plan, and scores tasks by impact and date urgency.
5. A reviewer confirms meaning, owners, dates, and authorization before any real action.

The engine does **not** call an AI model, interpret unstructured transcripts automatically, send messages, publish content, spend money, or update business systems.

## Capabilities

| Capability | Behavior |
| --- | --- |
| Evidence checks | Rejects missing sources and quotations absent from the source |
| Dependency graph | Rejects unknown IDs and cycles; returns prerequisite order |
| Priority scoring | Impact 1/3/5 + 4 overdue or + 2 due within two days |
| Missing details | Blocks tasks with an unconfirmed owner or due date |
| Approval gates | Blocks all external actions and high-impact internal work |
| Follow-up draft | Generates an editable recap from validated structured input |
| Traceability | Keeps source references beside each task and decision |

A task's priority is separate from execution order. A high-priority task can remain blocked by prerequisites. All tasks are treated as open; this prototype does not track completed work.

## Try the controls

- Change an evidence quote: the input is rejected.
- Add a dependency cycle: the input is rejected.
- Set an owner to null: the task is flagged for confirmation.
- Set `approved` to true on a publication task: it remains blocked. Input data cannot grant approval.

## Repository guide

- `src/socialclose_workflows/engine.py`: validation and report generator.
- `examples/meeting.json`: synthetic source plus structured extraction.
- `examples/expected/`: generated reference report and plan.
- `prompts/extract.md`: model-neutral extraction prompt.
- `tests/test_engine.py`: meaningful failure and approval tests.
- `docs/ARCHITECTURE.md`: boundaries and next implementation phases.
- `docs/REVIEW.md`: reviewer checklist and privacy limitations.

## Limits

Exact quotations demonstrate traceability, not semantic correctness. A valid quotation can still be misinterpreted or assigned to the wrong task. Humans must review the meaning. The `synthetic` flag is an author assertion, not a detector or sanitizer. Do not add real customer data, credentials, or private operational details to a public repository.

No redistribution license is granted in this version; choose one before offering public reuse.
