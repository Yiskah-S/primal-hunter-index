#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# tools/projector.py — deterministic replay of a character's knowledge state
#
# Contracts this obeys (and will yell about):
# - Timeline: event objects, event types, per-event source_ref[]  (v1.0)  :contentReference[oaicite:11]{index=11}
# - Source Ref: structure & scene spans (must have scene_id + lines)      :contentReference[oaicite:12]{index=12}
# - ID: IDs everywhere, no names, dot-separated namespaces                 :contentReference[oaicite:13]{index=13}
# - Provenance: timelines are truth for progression; no inline prov in canon  :contentReference[oaicite:14]{index=14}
# - Tagging: only approved tags should influence flags (mvp: ignore)       :contentReference[oaicite:15]{index=15}
# ─────────────────────────────────────────────────────────────────────────────

import argparse, json, re, sys
from pathlib import Path

SCENE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{2}$")  # dotted BB.CC.SS (we adopted this)
ID_RE     = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")  # validated after split by namespace

def _load_timeline(character_id: str, repo_root: Path) -> list[dict]:
    """Load and minimally validate a character timeline. We keep it boring on purpose."""
    p = repo_root / "records" / "characters" / character_id.split(".", 1)[-1] / "timeline.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("timeline.json must be an array of events (ordered)")
    for ev in data:
        # Must have IDs and receipts. Contracts are not suggestions.  :contentReference[oaicite:17]{index=17} :contentReference[oaicite:18]{index=18}
        event_id = ev.get("event_id")
        if not (isinstance(event_id, str) and event_id.startswith("ev.")):
            raise ValueError(f"bad event_id: {event_id!r}")
        scene_id = ev.get("scene_id")
        if not (isinstance(scene_id, str) and SCENE_RE.match(scene_id)):
            raise ValueError(f"scene_id must be BB.CC.SS, got {scene_id!r}")
        order = ev.get("order")
        if not (isinstance(order, int) and order >= 1):
            raise ValueError(f"order must be >=1, got {order!r}")
        sref = ev.get("source_ref")
        if not (isinstance(sref, list) and sref):
            raise ValueError(f"every event needs source_ref[] ({event_id})")
        for r in sref:
            # Minimal Source-Ref checks; full schema lives elsewhere.  :contentReference[oaicite:19]{index=19}
            if r.get("type", "scene") not in {"scene","wiki","user","inferred","external"}:
                raise ValueError(f"invalid source_ref.type in {event_id}")
            if r.get("type","scene") == "scene":
                sr_scene = r.get("scene_id","")
                if not SCENE_RE.match(sr_scene):
                    raise ValueError(f"source_ref.scene_id must be BB.CC.SS (event {event_id})")
                line_start = int(r.get("line_start",0))
                line_end = int(r.get("line_end",0))
                if line_start < 1 or line_end < line_start:
                    raise ValueError(f"invalid source_ref line range in {event_id}")
    return data

def _sort_key(ev: dict, view: str) -> tuple:
    """Stable ordering. Reader view = book order; character view prefers epistemic clock when present."""
    epi = ev.get("epistemic_at", {}).get("scene_id") if view == "character" else None
    s   = epi or ev["scene_id"]
    return (s, ev["order"], ev["event_id"])  # deterministic tie-breaker

def project(character_id: str, scene_id: str, *, view: str = "character", repo_root: Path = Path(".")) -> dict:
    """
    Reconstruct what <character_id> knows by <scene_id>.
    Output is boring-on-purpose: IDs, tiny fact dicts, and receipts.
    """
    events = sorted(_load_timeline(character_id, repo_root), key=lambda e: _sort_key(e, view))
    state = {"character": character_id, "scene": scene_id, "skills": {}, "flags": []}

    def add_evidence(node_id: str, ev: dict):
        s = state["skills"].setdefault(node_id, {"known": True, "facts": {}, "evidence": []})
        s["evidence"].extend(ev["source_ref"])

    def apply_delta(node_id: str, ev: dict):
        if not ev.get("knowledge_delta"):
            return
        entry = state["skills"].setdefault(node_id, {"known": True, "facts": {}, "evidence": []})
        for d in ev["knowledge_delta"]:
            entry["facts"][d["field_path"]] = d.get("new_value")

    def ensure_node_id(raw_id: str) -> str:
        if not isinstance(raw_id, str):
            raise ValueError(f"node id must be string, got {raw_id!r}")
        parts = raw_id.split(".")
        if len(parts) < 2 or parts[0] != "sn" or not all(ID_RE.match(p) for p in parts[1:]):
            raise ValueError(f"bad node id: {raw_id}")
        return raw_id

    for ev in events:
        # stop at the reveal cutoff for reader-view; character-view uses epistemic sort but same cutoff scene
        if ev["scene_id"] > scene_id:  # book anchor remains the cutoff; matches provenance thinking.  :contentReference[oaicite:20]{index=20}
            break
        t = ev.get("type")
        node = ev.get("node_id") or ev.get("skill_id")

        if t == "skill_acquired" and node:
            node_id = ensure_node_id(node)
            add_evidence(node_id, ev)
            apply_delta(node_id, ev)
        elif t == "skill_evolved" and node:
            node_id = ensure_node_id(node)
            add_evidence(node_id, ev)
            apply_delta(node_id, ev)
        elif t == "skill_upgraded":
            from_node = ev.get("from_node_id")
            to_node = ev.get("to_node_id")
            if not (from_node and to_node):
                raise ValueError(f"skill_upgraded event missing from/to node ids ({ev.get('event_id')})")
            from_node = ensure_node_id(from_node)
            to_node = ensure_node_id(to_node)
            if from_node in state["skills"]:
                prev = state["skills"].pop(from_node)
            else:
                prev = {"known": True, "facts": {}, "evidence": []}
            # carry evidence and facts forward
            current = state["skills"].setdefault(to_node, {"known": True, "facts": {}, "evidence": []})
            current["evidence"].extend(prev.get("evidence", []))
            current["evidence"].extend(ev["source_ref"])
            current["facts"].update(prev.get("facts", {}))
            apply_delta(to_node, ev)
        elif t in {"skill_observation", "belief_corrected"} and node:
            node_id = ensure_node_id(node)
            add_evidence(node_id, ev)
            apply_delta(node_id, ev)
        # Tags → flags (MVP: just copy; later we can gate by approval per Tagging Contract)  :contentReference[oaicite:22]{index=22}
        for tag in ev.get("tags", []):
            state["flags"].append(tag)

    # make flags predictable for diffs
    state["flags"] = sorted(set(state["flags"]))
    return state

def compare_before_after(character_id: str, topic_id_or_prefix: str, *, repo_root: Path, upgrade_predicate="skill_evolved"):
    """
    Compare earliest recovery-related evidence vs the upgrade event.
    Returns a tiny verdict struct the LLM can narrate with receipts.
    """
    events = _load_timeline(character_id, repo_root)
    def mentions_topic(ev: dict) -> bool:
        candidates = [
            ev.get("node_id"),
            ev.get("skill_id"),
            ev.get("from_node_id"),
            ev.get("to_node_id"),
        ]
        return any(isinstance(n, str) and n.startswith(topic_id_or_prefix) for n in candidates)

    # Filter candidates
    upgrades = [e for e in events if e.get("type") in {"skill_evolved","skill_upgraded"} and mentions_topic(e)]
    deltas   = []
    for e in events:
        if not mentions_topic(e): continue
        for d in e.get("knowledge_delta", []):
            if re.search(r"(recovery|regen)(_rate)?$", d["field_path"]):
                deltas.append((e, d))

    if not upgrades:
        return {"verdict": "no_upgrade_event"}

    sort_by_book = lambda ev: (ev["scene_id"], ev["order"], ev["event_id"])
    upgrades.sort(key=sort_by_book)
    deltas.sort(key=lambda t: sort_by_book(t[0]))
    up = upgrades[0]

    # Split suspicion vs confirmation (cheap but useful heuristic: confidence < 1.0 or inference note)
    suspicions = [(e,d) for (e,d) in deltas if (d.get("confidence", 1.0) < 1.0) or any(r.get("inference_type") for r in e.get("source_ref", []))]
    confirms   = [(e,d) for (e,d) in deltas if (d.get("confidence", 1.0) >= 1.0) and not any(r.get("inference_type") for r in e.get("source_ref", []))]

    first_sus = suspicions[0][0] if suspicions else None
    first_con = confirms[0][0] if confirms else None

    def pack(ev, d=None):
        if not ev: return None
        out = {"event_id": ev["event_id"], "scene_id": ev["scene_id"], "source_ref": ev["source_ref"]}
        if d: out["knowledge_delta"] = [d]
        return out

    if first_con and (first_con["scene_id"] < up["scene_id"] or (first_con["scene_id"] == up["scene_id"] and first_con["order"] < up["order"])):
        return {"verdict": "confirmed_before", "upgrade": pack(up), "first_confirmation": pack(first_con)}
    if first_con and first_con["scene_id"] > up["scene_id"] and first_sus and first_sus["scene_id"] < up["scene_id"]:
        return {"verdict": "suspected_before_confirmed_after", "upgrade": pack(up), "first_suspicion": pack(first_sus, suspicions[0][1]), "first_confirmation": pack(first_con, confirms[0][1])}
    if first_con:
        return {"verdict": "confirmed_after", "upgrade": pack(up), "first_confirmation": pack(first_con, confirms[0][1])}
    if first_sus:
        return {"verdict": "no_confirmation_evidence", "upgrade": pack(up), "first_suspicion": pack(first_sus, suspicions[0][1])}
    return {"verdict": "no_evidence", "upgrade": pack(up)}

def main():
    ap = argparse.ArgumentParser(description="PHI Projector — replay character knowledge")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("snapshot", help="state at scene")
    p1.add_argument("--character", required=True)
    p1.add_argument("--scene", required=True)   # dotted BB.CC.SS
    p1.add_argument("--view", choices=["reader","character"], default="character")

    p2 = sub.add_parser("compare", help="before/after verdict for a topic vs upgrade")
    p2.add_argument("--character", required=True)
    p2.add_argument("--topic", required=True)   # e.g., "sn.meditation." prefix
    args = ap.parse_args()

    root = Path(".")
    if args.cmd == "snapshot":
        print(json.dumps(project(args.character, args.scene, view=args.view, repo_root=root), indent=2))
    else:
        print(json.dumps(compare_before_after(args.character, args.topic, repo_root=root), indent=2))

if __name__ == "__main__":
    main()
