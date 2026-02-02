#!/usr/bin/env python3
"""
Send bulk emails automatically using Gmail API (OAuth) + attach a PDF resume.
No App Password needed.

First run opens a browser for consent and creates token.json.
Python 3.8+ recommended (works on 3.12 too)
"""

import time
import base64
from pathlib import Path
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

EMAIL_LIST_FILE = "emails.txt"
RESUME_FILE = "Teja K Data Engineer Resume.pdf"

SUBJECT = "Data Engineer – Open Roles | Resume Attached"
BODY = """Hi,

I hope you’re doing well.

I’m reaching out to check if you currently have any open or upcoming opportunities for a Data Engineer role.
I have experience building cloud-native data platforms, real-time and batch pipelines, and analytics solutions across GCP and AWS.

I’ve attached my resume for your reference.
Please let me know if there is a suitable role, or if you need any additional details from my side.

Thank you for your time.

Best regards,
Teja Kandukuri
"""

DELAY_SECONDS = 2
MAX_EMAILS = 3  # test first; set 0 to send all

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def load_emails(path: Path):
    emails = []
    seen = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line.strip()
        if not raw:
            continue
        # pull the last token that looks like an email
        tokens = [t.strip(" ,;") for t in raw.split()]
        candidate = ""
        for t in reversed(tokens):
            if "@" in t and "." in t.split("@", 1)[-1]:
                candidate = t
                break
        if not candidate:
            continue
        candidate = candidate.lower()
        if candidate not in seen:
            seen.add(candidate)
            emails.append(candidate)
    return emails


def get_gmail_service():
    token_path = Path("token.json")
    cred_path = Path("credentials.json")

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not cred_path.exists():
                raise FileNotFoundError("credentials.json not found (download OAuth Desktop credentials and save here).")
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def make_message(to_email: str, subject: str, body: str, attachment_path: Path):
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    data = attachment_path.read_bytes()
    msg.add_attachment(data, maintype="application", subtype="pdf", filename=attachment_path.name)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def main():
    emails_path = Path(EMAIL_LIST_FILE)
    resume_path = Path(RESUME_FILE)

    if not emails_path.exists():
        raise FileNotFoundError(emails_path)
    if not resume_path.exists():
        raise FileNotFoundError(resume_path)

    recipients = load_emails(emails_path)
    if MAX_EMAILS:
        recipients = recipients[:MAX_EMAILS]

    print(f"Sending {len(recipients)} emails via Gmail API (OAuth)...")
    service = get_gmail_service()

    for i, to_email in enumerate(recipients, start=1):
        try:
            message = make_message(to_email, SUBJECT, BODY, resume_path)
            service.users().messages().send(userId="me", body=message).execute()
            print(f"[{i}] SENT -> {to_email}")
        except HttpError as e:
            print(f"[{i}] FAIL -> {to_email} | Gmail API error: {e}")
        except Exception as e:
            print(f"[{i}] FAIL -> {to_email} | {e}")

        time.sleep(DELAY_SECONDS)

    print("✅ Done.")


if __name__ == "__main__":
    main()