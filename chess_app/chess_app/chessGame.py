from flask import Blueprint, request ,render_template,jsonify,url_for
import chess as chesslib
from stockfish import Stockfish

game = Blueprint("game", __name__, url_prefix="/game")
board = chesslib.Board()
engine = Stockfish(path="/opt/homebrew/bin/stockfish")
engine.set_skill_level(-1)
@game.route('/')
def index():
    board.reset()
    engine.set_position([])
    return render_template('chessboard.html')
    

@game.post('/move')
def move():
    data = request.get_json()
    source = data.get("from")
    target = data.get("to")

    if not source or not target:
        return jsonify({"status": "error", "message": "Invalid move input"})

    try:
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
            engine.set_fen_position(board.fen())
            engineMove = chesslib.Move.from_uci(engine.get_best_move()) 
            print(engineMove)
            board.push(engineMove)
            if checkmate(board):
                return checkmate(board)
         #   print('hi')
            return jsonify({"status": "ok", "fen": board.fen()})
        else:
            return jsonify({"status": "illegal"})

        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def checkmate(board):
    if board.outcome() is not None:
        if board.outcome() == chesslib.WHITE:
            return jsonify({"winner":"white"})
        if board.outcome() == chesslib.BLACK:
            return jsonify({"winner":"black"})
    return None