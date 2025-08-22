import os
import openai
from flask import Blueprint, request, Response
from app.models import SmsLog, db

# Initialize the SMS blueprint
sms_bp = Blueprint("sms", __name__)

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_ai_reply(message: str, user: str = None) -> tuple[str, str | None]:
    """Generate a reply from OpenAI's GPT model for an incoming SMS message."""
    openai.api_key = OPENAI_API_KEY
    system_prompt = (
        "You are the friendly digital assistant for Connect ATX Elite youth basketball fundraising. "
        "Respond helpfully and concisely. Suggest how to sponsor or learn more if asked."
    )
    try:
        # Make the API request to OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=80,
            temperature=0.6,
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        # Handle any potential errors gracefully
        return "Sorry, our AI is currently unavailable. Please visit connectatxelite.com.", str(e)

@sms_bp.route("/webhook", methods=["POST"])
def sms_webhook():
    """Handle incoming SMS messages and respond using AI-generated replies."""
    msg = request.form.get("Body", "").strip()
    from_num = request.form.get("From", "")
    to_num = request.form.get("To", "")

    # Get AI-generated reply based on the incoming message
    ai_reply, ai_error = get_ai_reply(msg, user=from_num)

    # Log the SMS and AI response in the database
    sms_log = SmsLog(
        from_number=from_num,
        to_number=to_num,
        message_body=msg,
        response_body=ai_reply,
        ai_used=True if not ai_error else False,
        error=ai_error
    )
    db.session.add(sms_log)
    db.session.commit()

    # Create the XML response for Twilio
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{ai_reply}</Message>
</Response>"""

    # Return the XML response to Twilio
    return Response(xml_response, mimetype="application/xml")

