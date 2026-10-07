from flask import Blueprint, request, jsonify
from app import db

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import User, Message

main = Blueprint("main", __name__)


@main.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "error": "Name and email are required"
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400

    if not email:
        return jsonify({"error": "Email cannot be empty"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "error": "User with this email already exists"
        }), 409

    user = User(
        name=name,
        email=email
    )

    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "User with this email already exists"
        }), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "error": "Database error"
        }), 500

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    }), 201

@main.route("/users", methods=["GET"])
def get_users():
    users = User.query.order_by(User.id).all()

    return jsonify([
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]), 200

@main.route("/messages", methods=["POST"])
def send_message():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    message_text = data.get("message")

    if sender_id is None or receiver_id is None or message_text is None:
        return jsonify({
            "error": "sender_id, receiver_id and message are required"
        }), 400

    message_text = message_text.strip()

    if not message_text:
        return jsonify({
            "error": "Message cannot be empty"
        }), 400

    if sender_id == receiver_id:
        return jsonify({
            "error": "Sender and receiver cannot be the same"
        }), 400

    sender = db.session.get(User, sender_id)
    receiver = db.session.get(User, receiver_id)

    if not sender:
        return jsonify({"error": "Sender not found"}), 404

    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    new_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message_text
    )

    try:
        db.session.add(new_message)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "error": "Database error"
        }), 500

    return jsonify({
        "message": "Message sent successfully",
        "data": {
            "id": new_message.id,
            "sender_id": new_message.sender_id,
            "receiver_id": new_message.receiver_id,
            "message": new_message.message,
            "created_at": new_message.created_at.isoformat()
        }
    }), 201

@main.route("/messages", methods=["GET"])
def get_messages():
    user1_id = request.args.get("user1_id", type=int)
    user2_id = request.args.get("user2_id", type=int)

    if user1_id is None or user2_id is None:
        return jsonify({
            "error": "user1_id and user2_id are required"
        }), 400

    if user1_id == user2_id:
        return jsonify({
            "error": "The two users must be different"
        }), 400

    user1 = db.session.get(User, user1_id)
    user2 = db.session.get(User, user2_id)

    if not user1 or not user2:
        return jsonify({
            "error": "One or both users not found"
        }), 404

    messages = Message.query.filter(
        (
            (Message.sender_id == user1_id) &
            (Message.receiver_id == user2_id)
        )
        |
        (
            (Message.sender_id == user2_id) &
            (Message.receiver_id == user1_id)
        )
    ).order_by(Message.created_at.asc()).all()

    return jsonify([
        {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "created_at": message.created_at.isoformat()
        }
        for message in messages
    ]), 200