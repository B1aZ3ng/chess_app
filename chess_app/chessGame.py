from flask import Blueprint, request, render_template, jsonify, redirect, url_for,current_app,session
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename    
from flask_socketio import emit, join_room
from stockfish import Stockfish
from datetime import datetime, UTC
import chess as chesslib
from chess_app import socketio, db, scheduler
from chess_app.models import ChessGame
import time
from flask_apscheduler import APScheduler # Scheduler for periodic tasks basically cleaning up boards
import random
waiting_player = None
waiting_room = None
import sys
sys.stdout.flush()
game = Blueprint("game", __name__, url_prefix="/game")

boards = {
    i: {
        "board": chesslib.Board(),
        "inGame": False,
        "engineLevel": None,
        "playerW": None,
        "playerB": None,
        "lastMoveTime": None,
    } for i in range(65536)
}

game.level = 20

engine = Stockfish(path="/opt/homebrew/bin/stockfish")

# @socketio.on('init')
# def socketStart(room):
#     if boards[room]["board"].move_stack == []:
#         engineMove(room)
    
@socketio.on('join')
def handle_join(data):
    room = int(data['room'])
    if current_user.is_authenticated:
        username = current_user.username 
    else:
        username = "Guest"
    join_room(room)
    board = boards[room]["board"]

    emit('status', {'msg': f"{username} joined {room}"}, room=room)
    emit('fen', {'fen': board.fen()}, room=room)

@socketio.on('move')
def socket_move(data):
    room = int(data.get("room"))
    if current_user.is_authenticated:
        username = current_user.username 
    else:
        return
    
    moveLen = len(boards[room]["board"].move_stack)
    if not (username == boards[room]["playerW"] and moveLen%2 == 0): 
        if not (username == boards[room]["playerB"] and moveLen%2 == 1): 
            return
        
    
    
    boards[room]["lastMoveTime"] = time.time()
    source = data.get("from")
    target = data.get("to")
    promotion = data.get("promotion", "")

    if not source or not target:
        emit('error', {'msg': 'Invalid move input'}, room=room)
        return

    board = boards[room]["board"]
    engineLevel = boards[room].get("engineLevel", None)
    uci = source + target + promotion
    move = chesslib.Move.from_uci(uci)

    if move in board.legal_moves:
        board.push(move)
        emit('valid', {
            'fen': board.fen(),
            'move': uci,
            'by': 'player'
        }, room=room)

        if board.is_game_over():
            if board.outcome().winner:
                outcome = "white"
            elif board.outcome().winner is False:
                outcome = "black"
            else:
                outcome = "draw"
            emit('game_over', {
                'fen': board.fen(),
                'winner': outcome
            }, room=room)
            addToDB(room, outcome)
            board.reset()
            boards[room]["engineLevel"] = None
            boards[room]["inGame"] = False
            return

        # Engine move
        if engineLevel:
            engineMove(room)    
        
        if board.is_game_over():
            if board.outcome().winner:
                outcome = "white by checkmate"
            elif board.outcome().winner is False:
                outcome = "black by checkmate"
            else:
                outcome = "draw"
            emit('game_over', {
                'fen': board.fen(),
                'winner': outcome
            }, room=room)
            addToDB(room, outcome)
            board.reset()
            boards[room]["engineLevel"] = None
            boards[room]["inGame"] = False
            return
          # Small delay to simulate thinking time
    else:
        emit('invalid', {'msg': 'Illegal move'}, room=room)

def engineMove(room, doEmit=True):
    engineLevel = boards[room].get("engineLevel", None)
    board = boards[room]["board"]
    engine.set_skill_level(engineLevel)
    engine.set_fen_position(board.fen())
    engine_move_uci = engine.get_best_move()
    engine_move = chesslib.Move.from_uci(engine_move_uci)
    if engine_move in board.legal_moves:
        boards[room]["board"].push(engine_move)
    if doEmit:
        emit('move', {
            'fen': board.fen(),
            'move': engine_move_uci,
            'by': 'engine'
        }, room=room)


def addToDB(room,outcome):
    board = boards[room]["board"]
    playerW = boards[room]["playerW"]
    playerB = boards[room]["playerB"]
    moves = ",".join([move.uci() for move in board.move_stack])
    cg = ChessGame(
        time=datetime.now(UTC),
        playerW=playerW if playerW else "NULL",
        playerB=playerB if playerB else "NULL",
        gameData=moves,
        outcome=outcome,
    )
    db.session.add(cg)
    db.session.commit()

@game.route('/', methods=['POST'])
@login_required
def postLevel():
    data = request.form
    level = int(data.get('level', 0))
    colour = data.get('startColour', None)
    if colour == "random":
        colour = "micah" if bool(random.randint(0, 1)) else "shelby"
    for i in range(65536):
        if not boards[i]["inGame"]:
            boards[i]["inGame"] = True
            boards[i]["engineLevel"] = level
            if colour == "micah" and level:
                if current_user.is_authenticated:
                    boards[i]["playerW"] = current_user.username
                else: 
                    boards[i]["playerW"] = "Guest"
                boards[i]["playerB"] = None
            elif colour == "shelby" and level:
                if current_user.is_authenticated:
                    boards[i]["playerB"] = current_user.username
                else: 
                    boards[i]["playerB"] = "Guest"
                boards[i]["playerW"] = None
                engineMove(i,doEmit=False)

            return redirect(url_for('game.start', room=i))

    return "No available room", 503


@game.route('/<int:room>')
@login_required
def start(room):
    boards[room]["lastMoveTime"] = time.time()
    if not boards[room].get("inGame", True): # Check if the game is already in progress and if not redirects to index or else it will glitch
        return redirect(url_for('main.index'))
    board = boards[room]["board"]
        
    username = current_user.username 
    if boards[room]["playerW"] == username:
        colour = "micah"
    elif boards[room]["playerB"] == username:
        colour = "shelby"
    else:
        colour = None
    return render_template(
        'chessboard.html',
        username=username   ,
        room=room,
        board=board.fen(),
        colour=colour,
        
    )


@scheduler.task('interval', id='cleanup_inactive_boards', seconds=1)  # Run every minute
# @socketio.on(None)
def cleanBoards():
    for i in range(65536):
        if boards[i]["inGame"] and boards[i]["lastMoveTime"]:
            elapsed = time.time() - boards[i]["lastMoveTime"]
            if elapsed > 120:  # 1 hour of inactivity
                boards[i]["board"].reset()
                boards[i]["inGame"] = False
                boards[i]["engineLevel"] = None
                boards[i]["playerW"] = None
                boards[i]["playerB"] = None
                boards[i]["lastMoveTime"] = None
                moveLen = len(boards[i]["board"].move_stack)
                outcome = "white by forfeit" if moveLen % 2 == 1 else "black by forfeit",
                # emit('game_over', {
                #     'fen': boards[i]["board"].fen(),
                #     'winner': outcome,
                #     'msg': 'Game ended due to inactivity'
                # }, room=i)
                addToDB(i, outcome)


@game.post("/startGame")
@login_required
def startGame():
    global waiting_player
    username = current_user.username

    for room in range(65536):
        if not boards[room]["inGame"]:
            break
    else:
        return "No rooms available", 503

    if waiting_player:
        # Match found
        opponent = waiting_player
        waiting_player = None

        # Random side assignment
        white, black = (username, opponent) if random.choice([True, False]) else (opponent, username)

        boards[room]["playerW"] = white
        boards[room]["playerB"] = black
        boards[room]["inGame"] = True
        boards[room]["engineLevel"] = None
        boards[room]["lastMoveTime"] = time.time()

        # Inform both players using session or other means
        if username == white:
            session['room'] = room
        return redirect(url_for('game.start', room=room))
    else:
        # No opponent yet
        waiting_player = username
        return render_template("waiting.html")  # A template that polls or waits for matchmaking

@game.get("/check_match")
@login_required
def check_match():
    username = current_user.username
    for room in range(65536):
        if boards[room]["playerW"] == username or boards[room]["playerB"] == username:
            if boards[room]["inGame"]:
                return jsonify({"found": True, "room": room})
    return jsonify({"found": False})