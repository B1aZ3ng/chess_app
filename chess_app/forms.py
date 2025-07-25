#!/usr/bin/env python3
"""
College navigator forms

@author: Roman Yasinovskyy
@version: 2025.7
"""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])


class SignupForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired()])
    name = StringField("name", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
