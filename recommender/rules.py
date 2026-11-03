"""Loads the rules and checks whether a rule applies to a patient and a movie.

Rule conditions are plain JSON (see data/rules.json). An unknown condition name raises an error,
so a typo in the rules file can't quietly switch a rule off."""
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent

PATIENT_KEYS = {"always", "age_lt", "age_gte", "sensitivity", "diagnosis_in", "treatment_phase"}
CONTENT_KEYS = {
    "flash_in", "flash_conf", "mpa_in", "runtime_gt", "runtime_lte", "runtime_missing",
    "pacing", "intensity", "theme_any", "accessibility_unknown", "accessibility_false", "any_of",
}


def load_rules(path: Path = ROOT / "data" / "rules.json") -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for r in data["rules"]:
        validate_rule(r)
    return data


def validate_rule(rule: Dict[str, Any]) -> None:
    bad_p = set(rule["patient_condition"]) - PATIENT_KEYS
    bad_c = _content_keys(rule["content_condition"]) - CONTENT_KEYS
    if bad_p or bad_c:
        raise ValueError(f"{rule['rule_id']}: unknown condition keys {bad_p | bad_c}")
    if rule["severity"] == "soft_penalty" and not isinstance(rule["penalty_weight"], (int, float)):
        raise ValueError(f"{rule['rule_id']}: soft rule needs numeric penalty_weight")
    if rule["severity"] == "hard_exclude" and rule["penalty_weight"] is not None:
        raise ValueError(f"{rule['rule_id']}: hard rule must not carry a penalty weight")
    if rule["justification_type"] not in ("sourced", "inferred_from_source", "inferred"):
        raise ValueError(f"{rule['rule_id']}: bad justification_type")


def _content_keys(cond: Dict[str, Any]) -> set:
    keys = set(cond)
    for sub in cond.get("any_of", []):
        keys |= _content_keys(sub)
    return keys


def patient_matches(cond: Dict[str, Any], p: Dict[str, Any]) -> bool:
    for key, val in cond.items():
        if key == "always":
            ok = bool(val)
        elif key == "age_lt":
            ok = p["age"] < val
        elif key == "age_gte":
            ok = p["age"] >= val
        elif key == "sensitivity":
            ok = val in p["known_sensitivities"]
        elif key == "diagnosis_in":
            ok = p["diagnosis_context"] in val
        elif key == "treatment_phase":
            ok = p["treatment_phase"] == val
        else:
            raise ValueError(f"unknown patient condition {key}")
        if not ok:
            return False
    return True


def content_matches(cond: Dict[str, Any], m: Dict[str, Any]) -> bool:
    tags = m["sensitivity_tags"]
    rt = m["runtime_minutes"]
    for key, val in cond.items():
        if key == "flash_in":
            ok = tags["flashing_strobe_content"] in val
        elif key == "flash_conf":
            ok = m["provenance"]["flashing"]["confidence"] == val
        elif key == "mpa_in":
            ok = m["mpa_rating"] in val
        elif key == "runtime_gt":
            ok = rt is not None and rt > val
        elif key == "runtime_lte":
            ok = rt is not None and rt <= val
        elif key == "runtime_missing":
            ok = (rt is None) == bool(val)
        elif key == "pacing":
            ok = tags["pacing_complexity"] == val
        elif key == "intensity":
            ok = tags["thematic_intensity"] == val
        elif key == "theme_any":
            ok = any(t in tags["theme_flags"] for t in val)
        elif key == "accessibility_unknown":
            ok = tags["accessibility"][val] is None
        elif key == "accessibility_false":
            ok = tags["accessibility"][val] is False
        elif key == "any_of":
            ok = any(content_matches(sub, m) for sub in val)
        else:
            raise ValueError(f"unknown content condition {key}")
        if not ok:
            return False
    return True


def evaluate_rules(rules: List[Dict[str, Any]], patient: Dict[str, Any], movie: Dict[str, Any]):
    """For each rule that applies to this patient: did this movie pass, get a penalty, or get removed?"""
    outcomes = []
    for r in rules:
        if not patient_matches(r["patient_condition"], patient):
            continue
        fired = content_matches(r["content_condition"], movie)
        if not fired:
            outcome, penalty = "pass", 0.0
        elif r["severity"] == "hard_exclude":
            outcome, penalty = "hard_exclude", None
        else:
            outcome, penalty = "soft_penalty", float(r["penalty_weight"])
        outcomes.append({
            "rule_id": r["rule_id"],
            "name": r["name"],
            "severity": r["severity"],
            "outcome": outcome,
            "penalty": penalty,
            "justification_type": r["justification_type"],
            "source": r["source"],
        })
    return outcomes


def hard_violations(rules: List[Dict[str, Any]], patient: Dict[str, Any], movie: Dict[str, Any]) -> List[str]:
    """IDs of the hard rules this movie breaks for this patient. Used by the final check and the tests."""
    return [
        r["rule_id"] for r in rules
        if r["severity"] == "hard_exclude"
        and patient_matches(r["patient_condition"], patient)
        and content_matches(r["content_condition"], movie)
    ]
