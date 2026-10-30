# Validation record

Eight unittest cases passed under Python 3.12.

Covered: valid planning and draft output; fabricated quotations; unknown sources and dependencies; dependency cycles; forged approval assertions across all external action types; unknown details and high-impact tasks; invalid dates and duplicate IDs; and non-synthetic input rejection.

The CLI generated the included reference JSON and Markdown successfully.

Example result: 5 tasks, 3 blocked, 1 overdue as of the fictional date 2027-01-11. No model or live connector integration was tested or implemented.
