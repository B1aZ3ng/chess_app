from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from flask_login import current_user 
from werkzeug.utils import secure_filename    
from flask_socketio import emit, join_room
from stockfish import Stockfish
from datetime import datetime,UTC
import chess as chesslib
from chess_app import socketio
from chess_app import db
from chess_app.models import ChessGame

game = Blueprint("game", __name__, url_prefix="/game")

boards = {i:{"board":chesslib.Board(), "inGame":False ,"engineLevel":None,"playerW":None,"playerB":None} for i in range (65536)}

game.level = 20

engine = Stockfish(path="/opt/homebrew/bin/stockfish")

@socketio.on('join')
def handle_join(data):
    room = int(data['room'])
    username = data.get("username", "Guest")
    join_room(room)
    board = boards[room]["board"]

    emit('status', {'msg': f"{username} joined {room}"}, room=room)
    emit('fen', {'fen': board.fen()}, room=room)

@socketio.on('move')
def socket_move(data):
    room = int(data.get("room"))
    print("room", room)
    source = data.get("from")
    target = data.get("to")
    promotion = data.get("promotion", "")
    print()
    if  not source or not target:
        print("error")
        emit('error', {'msg': 'Invalid move input'}, room=room)
        return

    board = boards[room]["board"]
    engineLevel = boards[room].get("engineLevel",None)
    uci = source + target + promotion
    move = chesslib.Move.from_uci(uci)
    print("move", move)
    if move in board.legal_moves:
        print("legal move")
        board.push(move)
        emit('valid',{
            'fen': board.fen(),
            'move': uci,
            'by': 'player'
        },
             room=room)
        if board.is_game_over():
            print("game over")
            outcome = board.outcome()
            winner = outcome.winner
            emit('game_over', {
                'fen': board.fen(),
                'winner': "draw" if winner is None else ("white" if winner else "black")
            }, room=room)
            addToDB(room)
            board.reset()
            boards[room]["engineLevel"] = None
            boards[room]["inGame"] = False
            
            return

        # Engine move
        if engineLevel:
            engine.set_skill_level(engineLevel)
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
        
        if board.is_game_over():
            print("game over")
            outcome = board.outcome()
            winner = outcome.winner
            emit('game_over', {
                'fen': board.fen(),
                'winner': "draw" if winner is None else ("white" if winner else "black")
            }, room=room)
            addToDB(room)
            board.reset()
            boards[room]["engineLevel"] = None
            boards[room]["inGame"] = False
            
            return
            
        
        

    else:
        emit('invalid', {'msg': 'Illegal move'}, room=room)

def addToDB(room):
    print( "adding to database...")
    board = boards[room]["board"]
    playerW,playerB = boards[room]["playerW"], boards[room]["playerB"]
    moves = ",".join([move.uci() for move in board.move_stack])
    print(moves)
    cg = ChessGame(
        time = datetime.now(UTC),
        playerW = playerW if playerW else "NULL",
        playerB = playerB if playerB else "NULL",
        gameData = moves,
        outcome = board.outcome().winner
    )
    print("added")
    db.session.add(cg)
    db.session.commit()




@game.post('/')
def postLevel():
    level = int(request.form.get('level', None))
    username=session.get('username', 'Guest')

    if session.get('room',None):
        return redirect(url_for('game.start', room=session.get('room', None)))
    
    for i in range (65536):
        if not boards[i]["inGame"]:
            print("starting game: room", i)
            boards[i]["inGame"] = True
            boards[i]["engineLevel"] = level
            session['room'] = i
            boards[i]["PlayerW"] = username
            boards[i]["PlayerB"] = None
            return redirect(url_for('game.start', room=i))
        
        
    

@game.route('/<int:room>')
def start(room):
    session['room'] = room
    board = boards[room]["board"]
    return render_template('chessboard.html', username=session.get('username', 'Guest'), room=room, board=board.fen())

