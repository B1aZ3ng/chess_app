#!/usr/bin/env python3
"""Working with SQLite3"""

import csv
from functools import cache
import logging
import sqlite3
from typing import Any

import click


@click.command(help="Create a database from the CSV file")
@click.argument("db_name")
@click.option("--datafile", default="menagerie.csv")
def createUserDB (db_name: str) -> None:
    """Create database"""
    print("CREATE")
    with sqlite3.connect(f"{db_name}.sqlite3") as connection:
        cur = connection.cursor()
        cur.execute(
            "CREATE table users ("
            + "username primary key,"
            + "passwordHash,"
            + "elo"
            + ")IF NOT EXISTS users;"
        )
        
def addUser(db_name,username,passwordHash,elo):
    with sqlite3.connect(f"{db_name}.sqlite3") as connection:
        cur = connection.cursor()
        res = cur.execute (f"SELECT username FROM users WHERE username = '{username}'")
        if res.fetchone() is None: #when user alr exists
            return False
        cur.execute(
        f"INSERT INTO users values({username},{passwordHash},{elo});"
        )


@click.command(help="Read all records from the specified table")
@click.argument("db_name")
@click.option("--table", "-t", default="animal")
@cache
def read(db_name: str, condition = "") -> None | list[Any]:
    """Read all records"""
    print("READ")
    with sqlite3.connect(f"{db_name}.sqlite3") as connection:
        connection.row_factory = sqlite3.Row
        cur = connection.cursor() 
        cur.execute(f"SELECT * FROM {db_name};")
    return cur.fetchall()


@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="animal")
@click.option("--location", "-l", default="", help="Location to read")
@click.option("--species", "-s", default="", help="Species to read")
def query(db_name: str, table: str, species: str, location: str) -> None:
    """Query records"""
    print("QUERY")


@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="animal")
@click.option("--animal", "-a", help="Animal to update", type=int, default=0)
def update(db_name: str, table: str, animal: int) -> None:
    """Update records"""
    print("UPDATE")


@click.command()
@click.argument("db_name")
@click.option("--table", "-t", default="animal")
@click.option("--animal", "-a", help="Animal to update", type=int, default=0)
@click.option("--species", "-s", default="", help="Species to delete")
def delete(db_name: str, table: str, animal: int, species: str) -> None:
    """Delete records"""
    print("DELETE")


@click.group()
@click.option("--verbose", "-v", is_flag=True, default=False)
def cli(verbose: bool):
    """Command-line interface"""
    if verbose:
        logging.basicConfig(level=logging.INFO)

createUserDB("test")