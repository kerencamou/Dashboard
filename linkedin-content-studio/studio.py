"""Offline LinkedIn content pack builder. Standard library only; never publishes."""
import argparse
import csv
import io
import json
import re
from datetime import date, timedelta
from pathlib import Path


class BriefError(ValueError):
    pass


def check(ok, message):
    if not ok:
        raise BriefError(message)


def build_pack(brief):
    check(isinstance(brief, dict), "Brief must be an object")
    check(brief.get("synthetic") is True, "Public demo accepts synthetic briefs only")
    for field in ("topic", "audience", "thesis", "question", "newsletter_title"):
        check(isinstance(brief.get(field), str) and brief[field].strip(), f"Missing {field}")
    voice = brief.get("voice", {})
    check(isinstance(voice, dict), "voice must be an object")
    banned = voice.get("banned_phrases", [])
    check(isinstance(banned, list) and all(isinstance(x, str) and x.strip() for x in banned), "Invalid banned phrases")
    claims = brief.get("claims")
    sources = brief.get("sources")
    check(isinstance(sources, dict) and sources and all(isinstance(k, str) and isinstance(v, str) for k,v in sources.items()), "Sources must map IDs to text")
    check(isinstance(claims, list) and len(claims) == 4, "Provide exactly four vetted claims")
    ids = set()
    for claim in claims:
        check(isinstance(claim, dict), "Claim must be an object")
        cid = claim.get("id")
        check(isinstance(cid, str) and cid and cid not in ids, "Claim IDs must be unique")
        ids.add(cid)
        sid, quote, text = claim.get("source_id"), claim.get("quote"), claim.get("text")
        check(isinstance(sid, str) and sid in sources, "Unknown source")
        check(isinstance(quote, str) and quote.strip() and quote in sources[sid], "Quote not found in source")
        check(isinstance(text, str) and text.strip(), "Claim text required")
    hooks = brief.get("hooks")
    check(isinstance(hooks, list) and len(hooks) == 7 and all(isinstance(h, str) and h.strip() for h in hooks), "Provide seven hooks")
    check(len({h.casefold().strip() for h in hooks}) == 7, "Hooks must be distinct")
    options = brief.get("poll_options")
    check(isinstance(options, list) and 2 <= len(options) <= 4 and all(isinstance(o, str) and o.strip() for o in options), "Provide 2–4 poll options")
    check(len({o.casefold().strip() for o in options}) == len(options), "Poll options must be distinct")
    try:
        start = date.fromisoformat(brief.get("start_date", ""))
    except (ValueError, TypeError) as exc:
        raise BriefError("Invalid start_date") from exc
    check(isinstance(brief.get("timezone"), str) and brief["timezone"].strip(), "Timezone label required")
    c = [x["text"] for x in claims]
    thesis, question = brief["thesis"], brief["question"]
    formats = ["insight", "contrarian", "checklist", "carousel_outline", "video_script", "poll", "newsletter_draft"]
    bodies = [
        f"{thesis}\n\n{c[0]}\n\n{c[1]}\n\n{question}",
        f"A different way to approach {brief['topic'].lower()}:\n\n{c[2]}\n\n{thesis}\n\n{question}",
        "A practical review checklist:\n\n" + "\n".join(f"{i+1}. {x}" for i,x in enumerate(c)) + f"\n\n{question}",
        f"Slide 1 — {thesis}\n" + "\n".join(f"Slide {i+2} — {x}" for i,x in enumerate(c)) + f"\nSlide 6 — {question}",
        f"[Opening]\n{thesis}\n\n[Main points]\n{c[0]}\n{c[2]}\n\n[Closing]\n{question}",
        f"{question}\n\n" + "\n".join(f"Option {i+1}: {x}" for i,x in enumerate(options)) + "\n\nShare the reason behind your choice in a comment.",
        f"{brief['newsletter_title']}\n\n{thesis}\n\n" + "\n\n".join(f"Principle {i+1}\n{x}" for i,x in enumerate(c)) + f"\n\nReflection\n{question}",
    ]
    refs = [[0,1], [2], [0,1,2,3], [0,1,2,3], [0,2], [], [0,1,2,3]]
    offsets = [0,2,4,7,9,11,13]  # Editorial suggestions, not publishing recommendations.
    assets = []
    for i, fmt in enumerate(formats):
        content = hooks[i] + "\n\n" + bodies[i]
        flags = ["Human review required: meaning, voice, claims, and final format"]
        for phrase in banned:
            if phrase.casefold() in content.casefold():
                flags.append("Banned phrase: " + phrase)
        if re.search(r"\b\d+(?:\.\d+)?\s*%", content):
            flags.append("Numeric percentage claim requires separate fact-check")
        assets.append({"id": f"LI-{i+1:02}", "format": fmt, "hook": hooks[i], "content": content,
                       "claim_ids": [claims[j]["id"] for j in refs[i]],
                       "suggested_date": (start + timedelta(days=offsets[i])).isoformat(),
                       "status": "draft", "publish_allowed": False, "review_flags": flags,
                       "characters": len(content), "words": len(content.split())})
    repetition = []
    for i,a in enumerate(assets):
        for b in assets[i+1:]:
            sa, sb = set(re.findall(r"\w+",a["content"].lower())), set(re.findall(r"\w+",b["content"].lower()))
            similarity = len(sa & sb) / len(sa | sb)
            if similarity >= .65:
                repetition.append({"assets": [a["id"],b["id"]], "token_overlap": round(similarity,2), "action": "Review angle and spacing; reuse is expected across formats"})
    return {"schema_version":"1.0", "synthetic":True, "topic":brief["topic"], "audience":brief["audience"],
            "timezone":brief["timezone"], "mode":"draft_only", "ai_provider_connected":False,
            "publishing_connected":False, "assets":assets, "claims":claims,
            "sources":sources, "repetition_review":repetition,
            "limits":"Templates render a human-vetted brief. Quotes are matched literally, not semantically verified. Counts are informational, not LinkedIn limit checks."}


def render(pack):
    lines = ["# LinkedIn multi-content pack", "", "SYNTHETIC DEMO · DRAFTS ONLY", "", f"Audience: {pack['audience']}", "", "All seven formats are review drafts. Carousel slides, video, and newsletter require production/editing.", ""]
    for asset in pack["assets"]:
        lines += [f"## {asset['id']} · {asset['format']}", "", f"Suggested date: {asset['suggested_date']} ({pack['timezone']}; no time scheduled)", "", asset["content"], "", "Evidence claim IDs: " + (", ".join(asset["claim_ids"]) or "Question only; no source-backed factual assertion selected"), "", "Review: " + "; ".join(asset["review_flags"]), ""]
    lines += ["## Source ledger", ""]
    for claim in pack["claims"]:
        lines += [f"- {claim['id']} ({claim['source_id']}): {claim['quote']}"]
    return "\n".join(lines) + "\n"


def calendar_csv(pack):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["asset_id","suggested_date","timezone","format","hook","status","publish_allowed"])
    for a in pack["assets"]:
        # Prevent spreadsheet formula execution if fields originate from an edited brief.
        values = [a["id"],a["suggested_date"],pack["timezone"],a["format"],a["hook"],"draft","false"]
        writer.writerow(["'"+v if v.lstrip().startswith(("=","+","-","@")) else v for v in values])
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        pack = build_pack(json.loads(args.brief.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, BriefError) as exc:
        parser.exit(2, f"Brief rejected: {exc}\n")
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in {"content_pack.json":json.dumps(pack,indent=2)+"\n", "content_pack.md":render(pack), "editorial_calendar.csv":calendar_csv(pack)}.items():
        (args.out/name).write_text(text,encoding="utf-8")
    print("Created seven draft assets, source ledger, review flags, and editorial calendar.")


if __name__ == "__main__":
    main()
