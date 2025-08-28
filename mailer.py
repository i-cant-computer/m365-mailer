from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field

import msal
import requests

import mailer_config

TIMEOUT = 5
HTTP_ACCEPTED = 202


@dataclass
class Mailer:
  """Sends emails using Microsoft's Graph API.

  See `Microsoft Identity Platform - Client Credentials Flow
  <https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow>`__
  for details of the OAuth2 client credentials flow.

  Attributes:
  tenant_id : the Azure Active Directory tenant (directory) ID.
  client_id : the application (client) ID registered in Azure AD.
  client_secret : the client secret generated for the application.
  scopes: a list of permission scopes for the Microsoft Graph API.

  """

  tenant_id: str
  client_id: str
  client_secret: str
  scopes: list[str] = field(
    default_factory=lambda: ["https://graph.microsoft.com/.default"]
  )

  def __post_init__(self) -> None:
    """Initialise a new Mailer for sending emails via Microsoft Graph API.

    Raises:
    ValueError: in the case of incorrect or invalid configuration.

    """
    self.log = logging.getLogger(__name__)
    app = msal.ConfidentialClientApplication(
      self.client_id,
      authority=f"https://login.microsoftonline.com/{self.tenant_id}",
      client_credential=self.client_secret,
    )

    result = app.acquire_token_for_client(scopes=self.scopes)

    if result is None:
      msg = "error retriving access token."
      self.log.error(msg)
      raise ValueError(msg)
    self.access_token = result["access_token"]

  def send_plaintext_email(
    self, from_addr: str, to_addr: str, subject: str, body: str
  ) -> None:
    """Send a plaintext email via Microsoft Graph API.

    Args:
      from_addr: the email address of the sender (must be a valid user in the
        configured Azure Active Directory tenant).
      to_addr: the recipient's email address.
      subject: the subject line of the email.
      body: the plaintext body content of the email.

    Raises:
      ValueError: in an email could not be delivered.

    """
    email_data = {
      "message": {
        "subject": f"{subject}",
        "body": {
          "contentType": "Text",
          "content": f"{body}",
        },
        "toRecipients": [{"emailAddress": {"address": f"{to_addr}"}}],
      },
      "saveToSentItems": "true",
    }
    headers = {
      "Authorization": f"Bearer {self.access_token}",
      "Content-Type": "application/json",
    }
    response = requests.post(
      f"https://graph.microsoft.com/v1.0/users/{from_addr}/sendMail",
      headers=headers,
      json=email_data,
      timeout=TIMEOUT,
    )
    if response.status_code != HTTP_ACCEPTED:
      msg = f"error sending email: recieved response {response.status_code} - {response.text}"
      self.log.error(msg)
      raise ValueError(msg)


def parse_args() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description="Send emails via Microsoft Graph API.")
  parser.add_argument(
    "-t",
    "--to",
    type=str,
    dest="to_addr",
    default=mailer_config.EMAIL_TO,
    help="the recipient's email address.",
  )
  parser.add_argument(
    "-f",
    "--from",
    type=str,
    dest="from_addr",
    default=mailer_config.EMAIL_FROM,
    help="the email address of the sender.",
  )
  parser.add_argument(
    "-s",
    "--subject",
    type=str,
    required=True,
    help="the subject line of the email.",
  )
  parser.add_argument(
    "-c",
    "--content",
    type=argparse.FileType("r", encoding="UTF-8"),
    default=sys.stdin,
    help="the plaintext body content of the email (file path or stdin).",
  )

  return parser.parse_args()


def main() -> None:
  """Entry point."""
  args = parse_args()
  mailer = Mailer(
    mailer_config.TENANT_ID, mailer_config.CLIENT_ID, mailer_config.CLIENT_SECRET
  )
  mailer.send_plaintext_email(
    args.from_addr,
    args.to_addr,
    args.subject,
    args.content.read(),
  )


if __name__ == "__main__":
  try:
    main()
  except Exception as error:  # noqa: BLE001
    log = logging.getLogger(__name__)
    msg = f"unexpected error: {error}"
    log.critical(msg, exc_info=True, stack_info=True)
    sys.exit(1)
