# LinkedIn Multi-Content Studio

**One vetted source → seven LinkedIn draft formats → an editorial review pack.**

A runnable portfolio prototype for multi-format content production. Every example is invented. It contains no real customers, personal stories, private content, or business results.

## Run

Python 3.10+, standard library only. From this folder:

```bash
python studio.py examples/brief.json --out output
python -m unittest discover -s tests -v
```

Open `output/content_pack.md`. Edit the structured brief and rerun to regenerate the pack. Reference output is included in `examples/expected/`.

## What it builds

| Asset | Intended editorial use |
| --- | --- |
| Insight post | Introduce the central idea |
| Contrarian post | Present a different angle without inventing a personal experience |
| Checklist | Make the idea actionable |
| Carousel outline | Supply slide copy for a designer |
| Video script | Supply speaking copy for recording |
| Poll | Invite a focused audience response |
| Newsletter draft | Arrange the source principles into an expandable article draft |

The outputs are starter drafts. The carousel is text, the video is a script, and the newsletter needs editorial expansion. No images, videos, slide files, or native LinkedIn objects are generated.

## Files generated

- `content_pack.md`: all seven editable drafts and source quotations.
- `content_pack.json`: drafts, claim references, counts, flags, and repetition review.
- `editorial_calendar.csv`: proposed dates over fourteen days, formats, and review states.

Calendar spacing is an illustrative editorial plan, not a claim about optimal LinkedIn timing. No posting times are scheduled. Character and word counts are informational and do not certify platform limits.

## Quality controls

- Rejects missing or fabricated evidence quotations and duplicate claim IDs.
- Requires seven distinct hooks and two to four distinct poll options.
- Flags configured banned phrases and numeric percentage claims for review.
- Reports token overlap between drafts to help review repetitive angles.
- Preserves draft-only status even if the input claims approval.
- Escapes spreadsheet formula prefixes in the CSV export.

Literal quotation checks cannot verify that a paraphrase is true, that a hook is supported, or that a source is reliable. A person must review every claim, hook, and CTA. The synthetic flag is an author assertion, not a data privacy detector.

## AI-assisted workflow

1. Prepare fictional source notes for public examples.
2. Use `prompts/content-strategy.md` with your preferred AI assistant to propose a brief.
3. Review and correct the brief's claims, hooks, tone, and question.
4. Run the local builder.
5. Review the output, refine repetitive posts, and produce the visual assets.
6. Approve and publish manually in a separate workflow.

The working code uses deterministic templates. There is no model API adapter, retrieval system, LinkedIn API integration, scheduler, analytics connection, or automatic publishing. Nothing is sent to an external service.

## Future implementation

- Provider adapter with structured output validation and explicit cost controls.
- Richer brand voice rules and distinct generation strategies per format.
- Human review screen showing claims beside their sources.
- Rendered carousel and video production workflow.
- Approved publishing adapter with payload-specific approval receipts.
- Manual performance import and learning loop, using authorized private data outside this public repository.

No platform performance, reach, or conversion claims are made. No redistribution license is granted in this draft.
