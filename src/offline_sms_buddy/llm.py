"""Talks to the local Ollama server. Nothing here uses the internet."""

import os
import re

import httpx
from dotenv import load_dotenv
from ollama import Client, ResponseError
from pydantic import ValidationError

from offline_sms_buddy.Model.SmsBuddyError import SmsBuddyError
from offline_sms_buddy.Model.SmsExplanation import SmsExplanation
from offline_sms_buddy.promts import PROMPT

# Settings come from the .env file in the project folder
load_dotenv()
MODEL = os.getenv("MODEL")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")


def explain_sms(sms: str) -> SmsExplanation:
    """Send the SMS to the local model and return the three-part explanation."""
    if not MODEL or not OLLAMA_HOST:
        raise SmsBuddyError(
            "Settings are missing. Please add MODEL and OLLAMA_HOST to the .env file."
        )

    client = Client(host=OLLAMA_HOST)

    try:
        response = client.chat(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT.format(sms=sms)}],
            format=SmsExplanation.model_json_schema(),  # force our JSON shape
            options={"temperature": 0.2},  
        )
    except (ConnectionError, httpx.ConnectError):
        raise SmsBuddyError(
            "The AI helper is not running. "
            "Please start Ollama and try again."
        )
    except ResponseError as e:
        if e.status_code == 404:
            raise SmsBuddyError(
                f"The AI model is not downloaded yet. "
                f"Run this once in a terminal: ollama pull {MODEL}"
            )
        raise SmsBuddyError(f"The AI helper had a problem: {e.error}")

    try:
        return SmsExplanation.model_validate_json(response.message.content)
    except ValidationError:
        raise SmsBuddyError(
            "The AI gave an answer in the wrong format. Please press the button again."
        )


# A simple check that doesn't depend on the AI. If the SMS has a link or
# mentions an OTP, we always show a warning, even if the model forgets to.
_RISK_PATTERNS = [
    r"https?://",
    r"\bwww\.",
    r"\bbit\.ly\b",
    r"\b\w+\.(com|in|xyz|link|top|info)/\S*",
    r"\bkyc\b",
    r"\bblock(ed)?\b",
    r"\bsuspend(ed)?\b",
    r"\bdisconnect(ed|ion)?\b",
    r"\bexpir(e|ed|es|y)\b",
    r"\b(immediately|urgent(ly)?|right now|today only)\b",
    r"\b(won|winner|lottery|prize|reward|cashback|refund)\b",
    r"\b(pin|password|cvv|aadhaar|pan card)\b",
]


def looks_risky(sms: str) -> bool:
    text = sms.lower()
    return any(re.search(p, text) for p in _RISK_PATTERNS)


def mentions_otp(sms: str) -> bool:
    return bool(re.search(r"\b(otp|one[- ]time password|verification code)\b", sms.lower()))