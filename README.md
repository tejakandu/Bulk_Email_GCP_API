# Bulk Email Sender using Gmail API (GCP)

This project sends bulk, personalized emails with attachments using the Gmail API and OAuth 2.0.

## Features
- Gmail API (OAuth) – no App Password required
- Bulk email sending with rate limiting
- Resume attachment support
- Safe for personal Gmail accounts

## Tech Stack
- Python 3
- Google Cloud Platform
- Gmail API
- OAuth 2.0

## Setup (High-level)
1. Create a Google Cloud project
2. Enable Gmail API
3. Configure OAuth consent screen
4. Create OAuth Client (Desktop app)
5. Download `credentials.json`
6. Run the script and authorize Gmail

> ⚠️ `credentials.json`, `token.json`, `emails.txt`, and resumes are intentionally excluded for security.

## Usage
```bash
python3 gmail_bulk_send_oauth.py