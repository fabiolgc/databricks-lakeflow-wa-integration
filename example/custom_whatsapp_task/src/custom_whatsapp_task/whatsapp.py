"""Lakeflow Integration: Send WhatsApp message via Twilio."""

import json

import requests
from databricks.lakeflow.integrations import integration


TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts"


@integration(display_name="Send WhatsApp message")
def send_whatsapp_message(
    to_phone_number: str,
    message: str,
    template_id: str,
    databricks_secrets_scope: str = "twilio",
):
    """Send a WhatsApp message using Twilio.

    Reads account_sid, auth_token, and from_number from the
    Databricks Secrets scope given by databricks_secrets_scope.
    """
    from databricks.sdk.runtime import dbutils

    sid = dbutils.secrets.get(scope=databricks_secrets_scope, key="account_sid")
    token = dbutils.secrets.get(scope=databricks_secrets_scope, key="auth_token")
    sender = dbutils.secrets.get(scope=databricks_secrets_scope, key="from_number")

    resp = requests.post(
        f"{TWILIO_API}/{sid}/Messages.json",
        data={
            "From": f"whatsapp:{sender}",
            "To": f"whatsapp:{to_phone_number}",
            "ContentSid": template_id,
            "ContentVariables": json.dumps({"1": message}),
        },
        auth=(sid, token),
        timeout=30,
    )

    if resp.status_code != 201:
        try:
            detail = resp.json().get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise Exception(f"Twilio error ({resp.status_code}): {detail}")

    body = resp.json()
    print(f"Sent! SID={body['sid']} status={body['status']} to={body['to']}")
