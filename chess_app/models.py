#!/usr/bin/env python3
"""
College navigator data models

@author: Roman Yasinovskyy
@version: 2025.7
"""

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from chess_app import db


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


class College(db.Model):
    username: Mapped[str] = mapped_column(primary_key=True)
    city: Mapped[str]
    state: Mapped[str]
