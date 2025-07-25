#!/usr/bin/env python3
"""
College navigator data models

@author: Roman Yasinovskyy
@version: 2025.7
"""
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from chess_app import db


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


class ChessGame(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[str] = Column(DateTime)
    player1: Mapped[str] 
    player2: Mapped[str]
    gameData : Mapped[str]
