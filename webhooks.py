from __future__ import annotations

import os
import hmac
import base64
import hashlib
import logging
import time
from collections import defaultdict, deque
from typing import Optional, Tuple

from flask import Blueprint, request, Response, current_app, abort, jsonify

from app.models import SmsLog, db

# ─────────────────────────────────────────────────────────────
# OpenAI client (new or legacy)
# ─────────────────────────────────────────────────────────────
_OPENAI_CLIENT = None
_OPENAI_LEGACY = False
try:
    from openai import OpenAI  # type: ignore
    _OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    try:
        import openai  # type: ignore
        openai.api_key = os.getenv("OPENAI_API_KEY")
        _OPENAI_LEGACY = True
        _OPENAI_CLIENT = openai
    except Exception:
        _OPENAI_CLIENT = None

sms_bp = Blueprint("sms", __name__)

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "120"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.6"))
OPENAI_TIMEOUT_SECS = float(os.getenv("OPENAI_TIMEOUT_SECS", "8"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "2"))

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
REQUIRE_TWILIO_SIGNATURE = os.getenv("REQUIRE_TWILIO_SIGNATURE", "0").lower() in {"1", "true", "yes"}

MAX_INBOUND_LEN = int(os.getenv("SMS_MAX_INBOUND_LEN", "800"))
MAX_OUTBOUND_LEN = int(os.getenv("SMS_MAX_OUTBOUND_LEN", "320"))

SITE_URL = os.getenv("SITE_URL", "https://connectatxelite.com")
DONATE_URL = os.getenv("DONATE_URL", f"{SITE_URL}/donate")
SPONSOR_URL = os.getenv("SPONSOR_URL", f"{SITE_URL}#sponsorships")
TRYOUTS_URL = os.getenv("TRYOUTS_URL", f"{SITE_URL}/calendar")

SYSTEM_PROMPT = os.getenv(
    "SMS_SYSTEM_PROMPT",
    (
        "You are the friendly digital assistant for Connect ATX Elite youth basketball fundraising. "
        "Answer concisely, be kind, and when it helps, point people to sponsor or learn more. "
        "If someone asks how to help, suggest sponsoring, donating, or sharing the program with a friend."
    ),
)

# Simple in-memory rate limiting per sender (best-effort)
RATE_LIMIT_WINDOW_SECS = int(os.getenv("SMS_RATE_WINDOW", "60"))
RATE_LIMIT_MAX_MSGS = int(os.getenv("SMS_RATE_MAX", "6"))
_rate_window: dict[str, deque[float]] = defaultdict(deque)

# ─────────────────────────────────────────────────────────────
# Utils
# ─────────────────────────────────────────────────────────────
def _xml_escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

def _trim(s: str, limit: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= limit else s[: max(0, limit - 1)] + "…"

def _verify_twilio_signature() -> None:
    if not REQUIRE_TWILIO_SIGNATURE or not TWILIO_AUTH_TOKEN:
        return
    sig = request.headers.get("X-Twilio-Signature", "")
    if not sig:
        abort(403)

    url = request.url
    params = request.form or {}
    pieces = [url] + [f"{k}{params[k]}" for k in sorted(params.keys())]
    body = "".join(pieces).encode("utf-8")
    digest = hmac.new(TWILIO_AUTH_TOKEN.encode("utf-8"), body, hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode("ascii")
    if not hmac.compare_digest(sig, expected):
        current_app.logger.warning("Twilio signature verification failed")
        abort(403)

def _rate_limited(sender: str) -> bool:
    if not sender:
        return False
    now = time.time()
    q = _rate_window[sender]
    # pop old
    while q and now - q[0] > RATE_LIMIT_WINDOW_SECS:
        q.popleft()
    if len(q) >= RATE_LIMIT_MAX_MSGS:
        return True
    q.append(now)
    return False

def _openai_chat(user_text: str) -> Tuple[str, Optional[str]]:
    if _OPENAI_CLIENT is None:
        return (f"Sorry, our AI is busy. You can sponsor or donate at {SITE_URL}.", "OpenAI client not initialized")
    last_err: Optional[str] = None
    for attempt in range(1, OPENAI_MAX_RETRIES + 2):
        try:
            if _OPENAI_LEGACY:
                resp = _OPENAI_CLIENT.ChatCompletion.create(  # type: ignore[attr-defined]
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_text},
                    ],
                    max_tokens=OPENAI_MAX_TOKENS,
                    temperature=OPENAI_TEMPERATURE,
                    request_timeout=OPENAI_TIMEOUT_SECS,
                )
                text = (resp.choices[0].message.content or "").strip()  # type: ignore[index]
            else:
                resp = _OPENAI_CLIENT.chat.completions.create(  # type: ignore[attr-defined]
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_text},
                    ],
                    max_tokens=OPENAI_MAX_TOKENS,
                    temperature=OPENAI_TEMPERATURE,
                    timeout=OPENAI_TIMEOUT_SECS,
                )
                text = (resp.choices[0].message.content or "").strip()  # type: ignore[index]

            if not text:
                text = f"Thanks for your message! You can sponsor or donate at {SITE_URL}."
            return (_trim(text, MAX_OUTBOUND_LEN), None)
        except Exception as e:
            last_err = str(e)
            current_app.logger.warning("OpenAI attempt %s failed: %s", attempt, last_err, exc_info=(attempt == OPENAI_MAX_RETRIES + 1))
    return (f"Thanks for reaching out! Learn more at {SITE_URL}.", last_err or "unknown error")

def _log_sms(message_sid: str | None, from_num: str, to_num: str, inbound: str, reply: str, ai_used: bool, err: Optional[str]) -> None:
    try:
        entry_kwargs = dict(
            from_number=from_num,
            to_number=to_num,
            message_body=inbound,
            response_body=reply,
            ai_used=ai_used,
            error=err,
        )
        # If your SmsLog has message_sid, store it (ignore if not)
        if message_sid and hasattr(SmsLog, "message_sid"):
            entry_kwargs["message_sid"] = message_sid  # type: ignore[assignment]
        db.session.add(SmsLog(**entry_kwargs))
        db.session.commit()
    except Exception as e:
        current_app.logger.error("Failed to log SMS: %s", e, exc_info=True)
        db.session.rollback()

def _twiml(msg: str) -> Response:
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{_xml_escape(msg)}</Message></Response>'
    return Response(xml, mimetype="application/xml")

# ─────────────────────────────────────────────────────────────
# Keyword handlers (STOP/HELP compliance + shortcuts)
# ─────────────────────────────────────────────────────────────
def _handle_keywords(text: str) -> Optional[str]:
    t = (text or "").strip().upper()
    # Twilio STOP/HELP conventions
    if t in {"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"}:
        return "You will no longer receive messages from us. Reply START to re-subscribe."
    if t in {"START", "YES", "UNSTOP"}:
        return "You have been re-subscribed. Text HELP for help."
    if t == "HELP":
        return f"Connect ATX Elite: Reply STOP to unsubscribe. Donate: {DONATE_URL} Sponsor: {SPONSOR_URL}"
    # Friendly shortcuts
    if t in {"DONATE", "DONATION"}:
        return f"Thanks for supporting! Donate here: {DONATE_URL}"
    if t in {"SPONSOR", "SPONSORSHIP"}:
        return f"We’d love to partner! Become a sponsor: {SPONSOR_URL}"
    if t in {"TRYOUT", "TRYOUTS", "SCHEDULE"}:
        return f"Tryouts & events: {TRYOUTS_URL}"
    return None

# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@sms_bp.route("/health", methods=["GET"])
def health() -> Response:
    status = {
        "status": "ok",
        "openai": bool(_OPENAI_CLIENT),
        "model": OPENAI_MODEL if _OPENAI_CLIENT else None,
        "twilio_sig_required": REQUIRE_TWILIO_SIGNATURE,
    }
    return Response(response=jsonify(status).get_data(), mimetype="application/json")

@sms_bp.route("/webhook", methods=["POST"])
def sms_webhook() -> Response:
    # Signature (optional)
    try:
        _verify_twilio_signature()
    except Exception:
        pass  # _verify_* will abort(403) when required

    msg = _trim(request.form.get("Body", "") or "", MAX_INBOUND_LEN)
    from_num = (request.form.get("From", "") or "").strip()
    to_num = (request.form.get("To", "") or "").strip()
    message_sid = (request.form.get("MessageSid", "") or "").strip()

    # Idempotency: if SmsLog has message_sid, skip duplicates
    if message_sid and hasattr(SmsLog, "message_sid"):
        try:
            exists = db.session.query(SmsLog).filter_by(message_sid=message_sid).first()
            if exists:
                return _twiml(_xml_escape(exists.response_body or ""))
        except Exception:
            db.session.rollback()

    # Rate limit
    if _rate_limited(from_num):
        reply = "You’re sending messages quickly. Please wait a moment and try again."
        _log_sms(message_sid, from_num, to_num, msg, reply, ai_used=False, err="rate_limited")
        return _twiml(reply)

    # Empty inbound
    if not msg:
        reply = f"Hi! Say DONATE, SPONSOR, or TRYOUTS. More: {SITE_URL}"
        _log_sms(message_sid, from_num, to_num, msg, reply, ai_used=False, err=None)
        return _twiml(reply)

    # Keyword handling (STOP/HELP + shortcuts)
    keyword_reply = _handle_keywords(msg)
    if keyword_reply is not None:
        _log_sms(message_sid, from_num, to_num, msg, keyword_reply, ai_used=False, err=None)
        return _twiml(keyword_reply)

    # AI
    ai_reply, ai_error = _openai_chat(msg)
    reply_text = ai_reply or f"Thanks for your message! Learn more at {SITE_URL}."
    _log_sms(message_sid, from_num, to_num, msg, reply_text, ai_used=ai_error is None, err=ai_error)

    return _twiml(reply_text)

