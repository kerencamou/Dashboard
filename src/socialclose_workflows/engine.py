"""Validate a structured AI draft against source evidence and produce a review plan."""
import argparse
import json
from datetime import date
from pathlib import Path


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def build_plan(data):
    require(isinstance(data, dict), "Input must be an object")
    require(data.get("schema_version") == "1.0", "Unsupported schema_version")
    require(data.get("synthetic") is True, "Public demo accepts synthetic data only")
    # This flag is an author assertion, not a privacy detector. Never publish real input.
    source = data.get("source")
    tasks = data.get("tasks")
    decisions = data.get("decisions", [])
    require(isinstance(source, dict) and source, "source must be a nonempty object")
    require(all(isinstance(k, str) and isinstance(v, str) and v for k, v in source.items()), "Source entries must be text")
    require(isinstance(tasks, list) and tasks, "tasks must be a nonempty list")
    require(isinstance(decisions, list), "decisions must be a list")
    require(isinstance(data.get("as_of"), str), "as_of is required")
    try:
        as_of = date.fromisoformat(data["as_of"])
    except ValueError as exc:
        raise ValidationError("Invalid as_of date") from exc

    def evidence(item):
        refs = item.get("evidence", [])
        require(isinstance(refs, list) and refs, "Each task/decision needs evidence")
        for ref in refs:
            require(isinstance(ref, dict), "Evidence must be an object")
            sid, quote = ref.get("source_id"), ref.get("quote")
            require(isinstance(sid, str) and sid in source, "Unknown source_id")
            require(isinstance(quote, str) and quote.strip() and quote in source[sid], "Evidence quote must exactly match source")

    ids = set()
    for task in tasks:
        require(isinstance(task, dict), "Task must be an object")
        tid = task.get("id")
        require(isinstance(tid, str) and tid and tid not in ids, "Task IDs must be unique nonempty strings")
        ids.add(tid)
        require(isinstance(task.get("title"), str) and task["title"].strip(), "Task title required")
        require(task.get("action") in {"internal", "send", "publish", "spend", "change_system"}, "Unknown action")
        require(task.get("impact") in {"low", "medium", "high"}, "Unknown impact")
        require(task.get("owner") is None or isinstance(task.get("owner"), str), "owner must be text or null")
        require(isinstance(task.get("approved", False), bool), "approved must be boolean")
        deps = task.get("depends_on", [])
        require(isinstance(deps, list) and all(isinstance(x, str) for x in deps), "Dependencies must be task IDs")
        require(len(deps) == len(set(deps)), "Duplicate dependency")
        due = task.get("due")
        require(due is None or isinstance(due, str), "due must be ISO date or null")
        if due is not None:
            try:
                date.fromisoformat(due)
            except ValueError as exc:
                raise ValidationError("Invalid task due date") from exc
        evidence(task)
    by_id = {t["id"]: t for t in tasks}
    for task in tasks:
        require(all(dep in ids for dep in task.get("depends_on", [])), "Unknown dependency")
    for decision in decisions:
        require(isinstance(decision, dict) and isinstance(decision.get("text"), str), "Decision text required")
        evidence(decision)

    order, active, done = [], set(), set()

    def visit(tid):
        require(tid not in active, "Dependency cycle detected")
        if tid in done:
            return
        active.add(tid)
        for dep in by_id[tid].get("depends_on", []):
            visit(dep)
        active.remove(tid)
        done.add(tid)
        order.append(tid)

    for tid in by_id:
        visit(tid)
    results = []
    for tid in order:
        task = by_id[tid]
        reasons = []
        if not task.get("owner") or not task["owner"].strip():
            reasons.append("Owner needs confirmation")
        if not task.get("due"):
            reasons.append("Due date needs confirmation")
        if task.get("depends_on"):
            reasons.append("Dependencies require verified completion: " + ", ".join(task["depends_on"]))
        sensitive = task["action"] != "internal" or task["impact"] == "high"
        if sensitive:
            # User-supplied approved=true is deliberately never trusted as authorization.
            reasons.append("Human approval must be obtained outside this demo")
        overdue = bool(task.get("due") and date.fromisoformat(task["due"]) < as_of)
        days = (date.fromisoformat(task["due"]) - as_of).days if task.get("due") else None
        score = {"low": 1, "medium": 3, "high": 5}[task["impact"]] + (4 if overdue else 2 if days is not None and days <= 2 else 0)
        results.append({**task, "status": "blocked" if reasons else "ready_for_internal_review", "blockers": reasons, "overdue": overdue, "priority_score": score})
    return {
        "schema_version": "1.0", "synthetic": True, "as_of": data["as_of"],
        "mode": "draft_only", "execution_enabled": False,
        "evidence_limit": "Exact quotations are checked; semantic accuracy still requires a person.",
        "decisions": decisions, "execution_order": order,
        "tasks": sorted(results, key=lambda t: -t["priority_score"]),
        "summary": {"total": len(results), "blocked": sum(bool(t["blockers"]) for t in results), "overdue": sum(t["overdue"] for t in results)},
    }


def markdown_report(plan):
    lines = ["# Synthetic meeting review", "", "DRAFT — human review required. No actions have been executed.", "", f"As of: {plan['as_of']}", "", "## Decisions", ""]
    lines += ["- " + d["text"] for d in plan["decisions"]]
    lines += ["", "## Prioritized tasks", ""]
    for task in plan["tasks"]:
        lines += [f"### {task['id']}: {task['title']}", "", f"Owner: {task.get('owner') or 'Unconfirmed'} | Due: {task.get('due') or 'Unconfirmed'} | Score: {task['priority_score']}", "", f"Status: {task['status']}", ""]
        lines += ["- " + reason for reason in task["blockers"]]
        lines += [f"- Evidence ({r['source_id']}): {r['quote']}" for r in task["evidence"]]
        lines += [""]
    lines += ["## Follow-up draft", "", "Hi team,", "", "Here are the decisions and next steps extracted from our synthetic demo meeting:", ""]
    lines += ["- " + d["text"] for d in plan["decisions"]]
    lines += [f"- {t['title']} — {t.get('owner') or 'owner to confirm'}; due {t.get('due') or 'date to confirm'}." for t in plan["tasks"]]
    lines += ["", "Please confirm responsibilities, dates, source interpretation, and approvals before proceeding.", "", "This is a generated draft; it has not been sent.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        plan = build_plan(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        parser.exit(2, f"Input rejected: {exc}\n")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    (args.out / "review.md").write_text(markdown_report(plan), encoding="utf-8")
    print(f"Draft generated: {args.out / 'review.md'}")


if __name__ == "__main__":
    main()
