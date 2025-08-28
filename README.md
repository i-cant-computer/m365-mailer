# M365 Mailer

A minimal script to send emails using Microsoft's Graph API.

This script:

- is contained in a single file, with minimal dependencies
- supports `text/plain` emails with arbitrary content from a file or stdin
- requires an active M365 subscription and additional configuration

---

## 🔧 Configuration

All settings are provided by a `mailer_config.py` file in the project root. A
`sample_mailer_config.py` is provided with illustrative values. Rename it and
tailor it to your needs.

Additional configuration inside M365 is required for the mailer to work. For
more information see
<https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow>.

---

## ▶️ Usage

Run the mailer from the command line with specific actions:

```bash
python3 mailer.py --help
```

**Options:**

```text
usage: mailer.py [-h] -t TO_ADDR -f FROM_ADDR -s SUBJECT [-c CONTENT]

Send emails via Microsoft Graph API.

options:
  -h, --help            show this help message and exit
  -t, --to TO_ADDR      the recipient's email address.
  -f, --from FROM_ADDR  the email address of the sender.
  -s, --subject SUBJECT
                        the subject line of the email.
  -c, --content CONTENT
                        the plaintext body content of the email (file path or stdin).
```

**Examples:**

- To send an email:

  ```bash
  python3 mailer.py -f "no-reply@example.com" -t "citizen@example.com" \
    -s "Email subject" --content body_content.txt
  ```

---

## 🗂 Structure

```text
.
├── README.md                 # This file
├── LICENSE                   # Project license
├── pyproject.toml            # Python Project file
├── mailer.py                 # Mailer script
├── mailer_config.py          # User-defined configuration (not committed)
├── sample_mailer_config.py   # Sample user-defined configuration
```

---

## ⚠️ Warnings

- Keep `mailer_config.py` protected from unauthorized access

---

## 📝 License

MIT License. See `LICENSE` for details.

---
