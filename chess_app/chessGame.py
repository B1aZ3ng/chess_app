from flask import Blueprint, request ,render_template,jsonify,url_for
import chess as chesslib
from stockfish import Stockfish
from datetime import datetime
from flask_socketio import emit, join_room
from chess_app import socketio


game = Blueprint("game", __name__, url_prefix="/game")
board = chesslib.Board()
engine = Stockfish(path="/opt/homebrew/bin/stockfish")
engine.set_skill_level(1)
game.level = 20
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{data['username']} joined {room}"}, room=room)


@socketio.on('move')
def handle_move(data):
    room = data['room']
    move = data['move']
    # Add your move logic here
    emit('move', {'move': move}, room=room)
    
@game.post('/')
def postLevel():
    print("hi")
    data = dict(request.form)
    return start(int(data['level']))

@game.route('/')
def start(level):
    engine.set_skill_level(level)
    board.reset()
    engine.set_position([])
    
    return render_template('chessboard.html')

@game.post('/move')
def move():
    data = request.get_json()
    source = data.get("from")
    target = data.get("to")
    promotion = data.get("promotion")
    if not source or not target:
        return jsonify({"status": "error", "message": "Invalid move input"})

    try:
        if promotion:
            move = chesslib.Move.from_uci(source + target + promotion)
        else:
            move = chesslib.Move.from_uci(source + target)
        move = chesslib.Move.from_uci(source + target)
        if board.outcome() is not None:
            if board.outcome() == chesslib.WHITE:
                return jsonify({"winner":"white"})
            if board.outcome() == chesslib.BLACK:
                return jsonify({"winner":"black"})
        if move in board.legal_moves:
        #    print(type(move))
            board.push(move)
            if checkmate(board):
                return checkmate(board)

            engineMove = getEngineMove(game.level,board.fen)
            print(engineMove)
            board.push(engineMove)
            print(board.outcome(),board.fen())
            if checkmate(board):
                return checkmate(board)
         #   print('hi')
            return jsonify({"status": "ok", "fen": board.fen(),"winner":"none"})
        else:
            return jsonify({"status": "illegal","winner":"none"})

        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def checkmate(board):
    outcome = board.outcome()
    print(outcome is not None)
    if outcome is not None:
        print(outcome)
        print("winner",outcome.winner)
        print("hi")
        if outcome.winner == chesslib.WHITE:
            return jsonify({"status": "ok", "fen": board.fen(),"winner":"white"})
        if outcome.winner == chesslib.BLACK:
            return jsonify({"status": "ok", "fen": board.fen(),"winner":"black"})
        else:
            return jsonify({"status": "ok", "fen": board.fen(),"winner":"someone"})
    return None

def getEngineMove(level,fen):
    engine.set_skill_level(level)
    engine.set_fen_position(fen())
    move = chesslib.Move.from_uci(engine.get_best_move())
    return move


def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S") 
