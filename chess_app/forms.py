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
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    


class SignupForm(FlaskForm):
    username = StringField("Enter an Username", validators=[DataRequired()])
    password = PasswordField("Enter a Password", validators=[DataRequired()])
    passwordAgain = PasswordField("Enter the Password Again", validators=[DataRequired()])
