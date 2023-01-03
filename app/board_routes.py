from app import db
from app.models.board import Board
from app.models.card import Card
from flask import Blueprint, request, jsonify, make_response, abort

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
    
    return make_response(jsonify(f"Board {new_board.title} successfully created"), 201)

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

### CARD-RELATED ROUTES ###

@boards_bp.route("/<board_id>/cards", methods=["POST"])
def create_card(board_id):
    
    board = validate_model(Board, board_id)
    
    request_body = request.get_json()
    new_card = Card(message=request_body["message"], likes_count=0, board=board)
    
    db.session.add(new_card)
    db.session.commit()
    return make_response(jsonify(f"Card {new_card.message} in {new_card.board.title} successfully created"), 201)

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