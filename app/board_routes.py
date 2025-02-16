from app import db
from app.models.board import Board
from app.models.card import Card
from flask import Blueprint, request, jsonify, make_response, abort
import os, requests

boards_bp = Blueprint("boards_bp", __name__, url_prefix="/boards")

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"message":f"{cls.__name__} {model_id} invalid"}, 400))

    model = cls.query.get(model_id)

    if not model:
        abort(make_response({"message":f"{cls.__name__} {model_id} not found"}, 404))

    return model

### BOARD ROUTES ###

@boards_bp.route("", methods=["POST"])
def create_board():
    request_body = request.get_json()
    new_board = Board.from_dict(request_body)
    
    db.session.add(new_board)
    db.session.commit()
    
    return make_response(jsonify(new_board.to_dict()), 201)

@boards_bp.route("", methods=["GET"])
def get_all_boards():
    
    boards = Board.query.all()
    
    boards_response = []
    for board in boards:
        boards_response.append(
            {
                "id": board.board_id,
                "title": board.title,
                "owner": board.owner
            }
        )
    return jsonify(boards_response)

@boards_bp.route("/<board_id>", methods=["GET"])
def get_one_board(board_id):
    board = validate_model(Board, board_id)
    return board.to_dict()

@boards_bp.route("/<board_id>", methods=["DELETE"])
def delete_board(board_id):
    board = validate_model(Board, board_id)
    
    for card in board.cards:
        db.session.delete(card)
    
    db.session.delete(board)
    db.session.commit()
    
    return make_response(jsonify(board.to_dict()), 200)

### CARD-RELATED ROUTES ###

@boards_bp.route("/<board_id>/cards", methods=["POST"])
def create_card(board_id):
    
    board = validate_model(Board, board_id)
    
    request_body = request.get_json()
    new_card = Card(message=request_body["message"], likes_count=0, board=board)
    
    db.session.add(new_card)
    db.session.commit()
    
    payload = {"channel": "llammmmas", "text": f"Card '{new_card.message}' successfully created!"}
    authorization = {"Authorization": f"Bearer {os.environ.get('SLACKBOT_AUTH_TOKEN')}"}
    requests.post('https://slack.com/api/chat.postMessage', params=payload, headers=authorization)
    
    return make_response(jsonify(new_card.to_dict()), 201)

@boards_bp.route("/<board_id>/cards", methods=["GET"])
def get_cards(board_id):
    
    board = validate_model(Board, board_id)
    
    cards_response = []
    for card in board.cards:
        cards_response.append(
            {
            "id": card.card_id,
            "likes_count": card.likes_count,
            "message": card.message,
            }
        )
    return jsonify(cards_response)