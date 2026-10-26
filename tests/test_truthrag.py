"""Unit tests: no network, no embedding model, no API key."""
import re

from truthrag.chunker import pack, sections
from truthrag.config import DEFAULTS
from truthrag.guard import check
from truthrag.index import tokenize
from truthrag.models import Answer, Chunk, Hit
from truthrag.redact import Redactor
from truthrag.retired import negation_re, states
from truthrag.retrieve import rrf, weight
from truthrag.truth import TruthClassifier

HALYARD = dict(DEFAULTS["truth"], header=r"<!--\s*CONTRACT:\s*(STATE|REFERENCE|LOG)\b",
               header_classes={"STATE": "current", "REFERENCE": "reference", "LOG": "log"},
               log_current_section=r"§\s*0\b", frontmatter_key="status",
               frontmatter_classes={"accepted": "current", "superseded": "archive"})


def test_header_classes_and_strips_comment():
    t = TruthClassifier(HALYARD).classify_doc(("docs", "a.md"), "<!-- CONTRACT: LOG — history. -->\n# T\nbody")
    assert t.truth == "log" and "CONTRACT" not in t.body and "# T" in t.body


def test_archive_folder_wins_over_header():
    t = TruthClassifier(HALYARD).classify_doc(("archive", "a.md"), "<!-- CONTRACT: STATE -->\n# T")
    assert t.truth == "archive"


def test_frontmatter_status_adr_style():
    text = "---\nstatus: superseded\n---\n# ADR-7\nWe chose X."
    t = TruthClassifier(HALYARD).classify_doc(("adr", "0007.md"), text)
    assert t.truth == "archive" and not t.body.startswith("---")


def test_log_current_section():
    c = TruthClassifier(HALYARD)
    assert c.classify_section("log", ["Log", "§0 CURRENT STATE"]) == "log_current"
    assert c.classify_section("log", ["Log", "§2 Revisions"]) == "log"


def test_sections_skip_headings_in_code():
    secs = sections("# T\n## A\nx\n```\n## not\n```\n### B\ny\n", {2, 3})
    assert [h for h, _ in secs] == [["T", "A"], ["T", "A", "B"]]


def test_pack_repeats_real_table_header_only():
    table = ["| a | b |", "|---|---|"] + [f"| {i} | {'x' * 30} |" for i in range(20)]
    parts = pack(table, 200)
    assert len(parts) > 1 and all(p.startswith("| a | b |\n|---|---|") for p in parts)


def test_tokenize_ids_and_parts():
    assert tokenize("CT-O3 full-scale") == ["ct-o3", "ct", "o3", "full-scale", "full", "scale"]


def test_weights_and_rrf():
    cfg = {"weights": DEFAULTS["weights"]}
    c = Chunk("x", "p", ["T"], "t", "archive", ["D8"], 1)
    assert weight(c, cfg) == 0.2 * 0.5
    assert rrf([1, None], 60) == 1 / 61


def test_states_respects_history_markers():
    neg = negation_re(DEFAULTS["truth"]["negation_markers"])
    p = re.compile(r"25 ?A")
    assert states(p, "The limit is 25 A.", neg)
    assert not states(p, "The limit was 25 A.", neg)
    assert not states(p, "Raised from 25 A, superseded by D8.", neg)


def test_redactor_and_guard():
    r = Redactor({"[customer]": ["Brightwater Robotics", "Brightwater"]})
    assert r("Brightwater Robotics and Brightwater's AGV") == "[customer] and [customer]'s AGV"
    hit = Hit(Chunk("x", "p", ["T"], "t", "current", [], 1))
    ans = check(Answer("q", "Brightwater uses 32 A [1][4].", citations=[1, 4], hits=[hit]), r)
    assert "citation [4] does not match a retrieved chunk" in ans.guard_issues
    assert "leak: [customer]" in ans.guard_issues and "Brightwater" not in ans.text
