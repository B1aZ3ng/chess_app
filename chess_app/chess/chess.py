from flask import Blueprint, request, jsonify
import chess

chess = Blueprint("chess", __name__, url_prefix="/game")

@chess.post("/move")
def move():
    data = request.get_json()
    print(data)