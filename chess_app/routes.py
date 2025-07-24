#!/usr/bin/env python3

from flask import Blueprint, abort, current_app, render_template, request, session


main = Blueprint("main", __name__, url_prefix="/")


@main.get("/")
def index():
    return render_template("index.html")





