from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SelectField,
    DateField,
    IntegerField,
)
from wtforms.validators import Optional, DataRequired, NumberRange, Length
from datetime import datetime, timedelta


class LoginForm(FlaskForm):
    email = EmailField("Email")
    password = PasswordField("Password")


class LoginUpdateForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )


class PersonalInfoForm(FlaskForm):
    birth_year = IntegerField(
        "Birth Year",
        validators=[Optional(), NumberRange(min=1900, max=datetime.now().year)],
    )
    sex = SelectField(
        "Sex", choices=["", "Male", "Female", "Other"], validators=[Optional()]
    )
    race = SelectField(
        "Race",
        choices=[
            "",
            "American Indian/Alaska Native",
            "Asian",
            "Black",
            "Pacific Islander",
            "White",
            "Other",
        ],
        validators=[Optional()],
    )
    ethnicity = SelectField(
        "Ethnicity", choices=["", "Hispanic", "Non-Hispanic"], validators=[Optional()]
    )

    def __repr__(self) -> str:
        return f"<RegisterForm email: {self.email.data}> password: {self.password.data} birth year: {self.birth_year.data} sex: {self.sex.data} race: {self.race.data} ethnicity: {self.ethnicity.data}"


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
        ],
    )
    birth_year = IntegerField(
        "Birth Year",
        validators=[Optional(), NumberRange(min=1900, max=datetime.now().year)],
    )
    sex = SelectField(
        "Sex", choices=["", "Male", "Female", "Other"], validators=[Optional()]
    )
    race = SelectField(
        "Race",
        choices=[
            "",
            "American Indian/Alaska Native",
            "Asian",
            "Black",
            "Pacific Islander",
            "White",
            "Other",
        ],
        validators=[Optional()],
    )
    ethnicity = SelectField(
        "Ethnicity", choices=["", "Hispanic", "Non-Hispanic"], validators=[Optional()]
    )

    def __repr__(self) -> str:
        return f"<RegisterForm email: {self.email.data}> password: {self.password.data} birth year: {self.birth_year.data} sex: {self.sex.data} race: {self.race.data} ethnicity: {self.ethnicity.data}"


class SearchForm(FlaskForm):
    start_date = DateField(
        "Start Date", default=lambda: datetime.now().date() - timedelta(days=28)
    )
    end_date = DateField("End Date", default=lambda: datetime.now().date())
    address = StringField("Address", render_kw={"list": "address-suggestions"})
