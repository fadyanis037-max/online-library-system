from flask import Blueprint, jsonify, request

from models import db, User


bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("/")
def list_users():
    users = [u.to_dict() for u in User.query.order_by(User.id.asc()).all()]
    return jsonify({"items": users, "count": len(users)})


@bp.post("/")
def create_user():
    data = request.get_json(force=True) or {}
    required = ["name", "email", "password"]
    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "Missing required fields: name, email, password"}), 400

    # Very basic example; production code should hash passwords
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=data["name"], email=data["email"], password=data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

