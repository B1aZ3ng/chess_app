from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename    
from flask_socketio import emit, join_room
from stockfish import Stockfish
from datetime import datetime
import chess as chesslib
from chess_app import socketio

game = Blueprint("game", __name__, url_prefix="/game")

boards = {}  # room_id -> { 'board': chess.Board, 'engine': Stockfish }
game.level = 20

def get_room_state(room):
    if room not in boards:
        board = chesslib.Board()
        engine = Stockfish(path="/opt/homebrew/bin/stockfish")
        engine.set_skill_level(game.level)
        boards[room] = {"board": board, "engine": engine}
    return boards[room]["board"], boards[room]["engine"]

@socketio.on('join')
def handle_join(data):
    room = str(data['room'])
    username = data.get("username", "Guest")
    join_room(room)
    board, _ = get_room_state(room)

    emit('status', {'msg': f"{username} joined {room}"}, room=room)
    emit('fen', {'fen': board.fen()}, room=room)

@socketio.on('move')
def socket_move(data):
    room = str(data.get("room"))
    source = data.get("from")
    target = data.get("to")
    promotion = data.get("promotion", "")

    if not room or not source or not target:
        emit('error', {'msg': 'Invalid move input'}, room=room)
        return

    board, engine = get_room_state(room)
    uci = source + target + promotion
    move = chesslib.Move.from_uci(uci)

    if move in board.legal_moves:
        board.push(move)
        emit('valid',{
            'fen': board.fen(),
            'move': uci,
            'by': 'player'
        },
             room=room)
        if board.is_game_over():
            outcome = board.outcome()
            winner = outcome.winner
            emit('game_over', {
                'fen': board.fen(),
                'winner': "draw" if winner is None else ("white" if winner else "black")
            }, room=room)
            return

        # Engine move
        engine.set_fen_position(board.fen())
        engine_move_uci = engine.get_best_move()
        engine_move = chesslib.Move.from_uci(engine_move_uci)

        if engine_move in board.legal_moves:
            board.push(engine_move)

        emit('move', {
            'fen': board.fen(),
            'move': engine_move_uci,
            'by': 'engine'
        }, room=room)
    else:
        emit('invalid', {'msg': 'Illegal move'}, room=room)



@game.post('/')
def postLevel():
    level = int(request.form.get('level', game.level))
    game.level = level
    return redirect(url_for('game.start', room=session.get('room', 'default')))

@game.route('/<room>')
def start(room):
    session['room'] = room
    board, engine = get_room_state(room)
    engine.set_skill_level(game.level)
    return render_template('chessboard.html', username=session.get('username', 'Guest'), room=room, board=board.fen())

