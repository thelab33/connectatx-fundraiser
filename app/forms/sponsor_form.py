from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SponsorForm(FlaskForm):
    name = StringField(
        "Your Name or Company",
        validators=[
            DataRequired(message="Name is required."),
            Length(max=80, message="Name must be under 80 characters."),
        ],
        render_kw={"placeholder": "Jane Doe or Acme Inc."},
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email."),
        ],
        render_kw={"placeholder": "you@example.com"},
    )

    amount = DecimalField(
        "Amount (USD)",
        validators=[
            DataRequired(message="Donation amount is required."),
            NumberRange(min=1, message="Minimum amount is $1."),
        ],
        places=2,
        render_kw={"placeholder": "100.00"},
    )

