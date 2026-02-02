#!/usr/bin/env python3
"""
Telegram JSON -> Extract emails from messages mentioning "Data Engineer family" roles
Output CSV: email,first_name,company,custom_line

Usage:
  python3 dejobsextracts.py data/result.json -o contacts.csv
"""

import json
import csv
import re
import argparse
from pathlib import Path
from typing import Any, Dict, List


def flatten_text(text_field: Any) -> str:
    if text_field is None:
        return ""
    if isinstance(text_field, str):
        return text_field
    if isinstance(text_field, list):
        parts: List[str] = []
        for item in text_field:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(text_field)


# -------------------- DATA-ENGINEER-FAMILY ROLE REGEX --------------------
# Notes:
# - case-insensitive
# - supports hyphen/underscore/space variations
# - tries to keep it "DE-ish" (doesn't match generic "engineer" alone)
DE_FAMILY_RE = re.compile(
    r"""
    (?ix)

    # 1) Core: Data Engineer (and variants)
    \bdata[\s_-]*engineer\b
    |
    \bdata\W*eng\b
    |
    \bde\b\W*(?:role|position|opening|job|hiring|req|requirement)?\b
    |
    # 2) Big Data Engineer
    \bbig\W*data\W*engineer\b
    |
    # 3) ETL roles
    \betl\W*(?:engineer|developer|dev)\b
    |
    # 4) Data Warehouse / DWH
    \bdata\W*(?:warehouse|warehousing)\W*(?:engineer|dev|developer)\b
    |
    \bdwh\W*(?:engineer|dev|developer)\b
    |
    # 5) Analytics Engineer
    \banalytics\W*engineer\b
    |
    # 6) BI Engineer
    \b(?:bi|business\W*intelligence)\W*engineer\b
    |
    # 7) Data Platform Engineer
    \bdata\W*platform\W*engineer\b
    |
    # 8) Data Pipeline / Pipeline Engineer (data context)
    \bdata\W*pipeline\W*engineer\b
    |
    # 9) Cloud Data Engineer
    \b(?:aws|gcp|google\W*cloud|azure)\W*data\W*engineer\b
    |
    \bcloud\W*data\W*engineer\b
    |
    # 10) Common DE tech-title engineers (optional but usually DE-like)
    \b(?:spark|hadoop|kafka)\W*engineer\b
    """,
    flags=re.IGNORECASE | re.VERBOSE
)
# ------------------------------------------------------------------------


EMAIL_RE = re.compile(
    r"""(?ix)
    (?<![\w.+-])
    ([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})
    (?![\w.+-])
    """
)


def extract_emails_list(text: str) -> List[str]:
    seen = set()
    out: List[str] = []
    for m in EMAIL_RE.finditer(text):
        e = m.group(1).strip().strip(".,;:()[]{}<>\"'")
        if e and e.lower() not in seen:
            seen.add(e.lower())
            out.append(e)
    return out


NAME_NEAR_EMAIL_RE = re.compile(r"(?i)([A-Za-z][A-Za-z .'-]{1,40})\s*<?\s*$")


def guess_first_name(text: str, email: str) -> str:
    # try to find "Name <email>"
    idx = text.lower().find(email.lower())
    if idx != -1:
        left = text[max(0, idx - 60):idx].strip()
        left = re.sub(r"[\(\[\{<,:;|\-]+\s*$", "", left).strip()
        m = NAME_NEAR_EMAIL_RE.search(left)
        if m:
            name = m.group(1).strip()
            first = re.split(r"\s+", name)[0].strip(".,;:-_()[]{}<>\"'")
            if first and len(first) >= 2:
                return first.title()

    # fallback: derive from email local-part
    local = email.split("@", 1)[0].split("+", 1)[0]
    token = re.split(r"[._\-]+", local)[0]
    token = re.sub(r"[^A-Za-z]", "", token)
    return token.title() if token else "there"


def guess_company_from_email(email: str) -> str:
    try:
        domain = email.split("@", 1)[1].lower()
        parts = [p for p in domain.split(".") if p]
        if len(parts) >= 2:
            candidate = parts[-2]  # amazon.com -> amazon ; microsoft.co.uk -> microsoft
        else:
            candidate = parts[0]
        candidate = candidate.replace("-", " ").replace("_", " ").strip()
        return candidate.title()
    except Exception:
        return ""


def build_custom_line(chat_name: str, message_text: str) -> str:
    snippet = re.sub(r"\s+", " ", message_text).strip()
    if len(snippet) > 140:
        snippet = snippet[:137] + "..."
    return f"Saw your message in the '{chat_name}' Telegram group about data engineering-related roles: “{snippet}”"


def extract_contacts(data: Dict[str, Any]) -> List[Dict[str, str]]:
    chat_name = data.get("name", "")
    seen_emails = set()
    contacts: List[Dict[str, str]] = []

    for msg in data.get("messages", []):
        if msg.get("type") != "message":
            continue

        text = flatten_text(msg.get("text")).strip()
        if not text:
            continue

        # ✅ Filter only DE-family related messages
        if not DE_FAMILY_RE.search(text):
            continue

        emails = extract_emails_list(text)
        if not emails:
            continue

        for email in emails:
            key = email.lower()
            if key in seen_emails:
                continue
            seen_emails.add(key)

            contacts.append({
                "email": email,
                "first_name": guess_first_name(text, email),
                "company": guess_company_from_email(email),
                "custom_line": build_custom_line(chat_name, text),
            })

    return contacts


def main():
    parser = argparse.ArgumentParser(description="Extract DE-family contacts from Telegram JSON.")
    parser.add_argument("json_file", help="Telegram export JSON file (e.g., data/result.json)")
    parser.add_argument("-o", "--output", default="contacts.csv", help="Output CSV (default: contacts.csv)")
    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rows = extract_contacts(data)

    out_path = Path(args.output)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "first_name", "company", "custom_line"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✔ Extracted {len(rows)} unique DE-family emails")
    print(f"📄 Saved to: {out_path.resolve()}")


if __name__ == "__main__":
    main()