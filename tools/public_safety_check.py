"""Review the public project tree for files and text that need safety attention."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".py", ".md", ".txt", ".csv", ".json", ".toml", ".yml", ".yaml"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "outputs"}
PUBLIC_DOC_NAMES = {
    "README.md",
    "PROJECT_STATUS.md",
    "PUBLIC_SHOWCASE_MANIFEST.md",
}

PATTERNS = {
    "OPENAI_API_KEY": re.compile(r"\bOPENAI_API_KEY\b", re.I),
    "api_key": re.compile(r"\bapi[_-]?key\b", re.I),
    "secret": re.compile(r"\bsecret\b", re.I),
    "password": re.compile(r"\bpasswords?\b", re.I),
    "token": re.compile(r"\btokens?\b", re.I),
    "private_key": re.compile(r"\bprivate[_ -]?key\b", re.I),
    "passport": re.compile(r"\bpassport\b", re.I),
    "student_id": re.compile(r"\bstudent[_ -]?id\b", re.I),
    "visa number": re.compile(r"\bvisa\s+number\b", re.I),
    "phone number": re.compile(r"\bphone\s+number\b|(?:\+?61|0)4\d{8}\b", re.I),
    "home address": re.compile(r"\bhome\s+address\b", re.I),
    "linkedin cookie": re.compile(r"\blinkedin\s+cookie\b", re.I),
    "seek login": re.compile(r"\bseek\s+login\b", re.I),
    "indeed login": re.compile(r"\bindeed\s+login\b", re.I),
    "auto apply": re.compile(r"\bauto[ -]?apply\b", re.I),
    "scraping login": re.compile(r"\bscraping\s+login\b", re.I),
}

NEGATIVE_CONTEXT = re.compile(
    r"\b(no|not|never|without|avoid|exclude|excluded|ignore|ignored|forbid|forbidden|"
    r"must not|do not|does not|should not|cannot|can't|won't|remove|redact)\b",
    re.I,
)


def is_skipped(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    parts = relative.parts
    if any(part in SKIP_DIRS for part in parts[:-1]):
        return True
    return len(parts) >= 2 and parts[0] == "data" and parts[1] == "private"


def is_documentation(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    return relative.parts[0] in {"docs", "portfolio"} or relative.name in PUBLIC_DOC_NAMES


def iter_public_text_files():
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return [], [(0, f"unreadable text file: {exc}", "read_error")]

    review_terms: set[str] = set()
    action_items: list[tuple[int, str, str]] = []
    documentation = is_documentation(path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        matched = [name for name, pattern in PATTERNS.items() if pattern.search(line)]
        if not matched:
            continue
        if documentation or NEGATIVE_CONTEXT.search(line):
            review_terms.update(matched)
        else:
            action_items.append((line_number, line.strip()[:160], ", ".join(matched)))
    return sorted(review_terms), action_items


def main() -> int:
    review_warnings: dict[Path, set[str]] = defaultdict(set)
    action_warnings: list[tuple[Path, int, str, str]] = []

    for path in iter_public_text_files():
        review_terms, action_items = scan_file(path)
        if review_terms:
            review_warnings[path].update(review_terms)
        for line_number, line, terms in action_items:
            action_warnings.append((path, line_number, line, terms))

    for path in sorted(review_warnings):
        relative = path.relative_to(PROJECT_ROOT)
        terms = ", ".join(sorted(review_warnings[path]))
        print(f"WARNING [review] {relative}: safety-boundary terms mentioned ({terms})")

    for path, line_number, line, terms in action_warnings:
        relative = path.relative_to(PROJECT_ROOT)
        print(f"WARNING [action] {relative}:{line_number}: {terms}: {line}")

    if action_warnings:
        print(f"WARNING: {len(action_warnings)} publish-blocking item(s) require review.")
        return 1

    print(
        "PASS: no publish-blocking secrets or private-data patterns found "
        f"({len(review_warnings)} documentation/context warning file(s) reviewed)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
