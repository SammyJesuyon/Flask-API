import os

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import validators
from validate import (validate_email_and_password, validate_template,
                      validate_user)

load_dotenv()

app = Flask(__name__)

#generated using secrets.token_hex(16) from the python secrets library
SECRET_KEY = os.environ.get("SECRET_KEY") or "this is a secret"

app.config["SECRET_KEY"] = SECRET_KEY

from models import Templates, User, user_collection

from utils import token_required

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/register", methods=["POST"])
def add_user():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    password = request.json['password']
    if len(password)<6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    if not first_name.isalpha() or not last_name.isalpha() or " " in first_name or " " in last_name:
        return jsonify({"message": "Please verify that you have a correct name and no spaces in between"}), 400
    if not validators.email(email):
        return jsonify({"message": "Please verify that you have a correct email"}), 400
    if user_collection.find_one({"email": email}):
        return jsonify({"message": "Email already exists"}), 400
    user = User()
    user.create(first_name=first_name, last_name=last_name, email=email, password=password)
    return jsonify({"message": "User created successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request",
            }, 400
        user = User().login(data["email"], data["password"])
        if user:
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode(
                    {"user_id": user["_id"]}, app.config["SECRET_KEY"], algorithm="HS256"
                )
                return {"message": "Successfully Logged In", "data": user}
            except Exception as e:
                return {"error": "Something went wrong", "message": str(e)}, 500
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized",
        }, 404
    except Exception as e:
        return {"message": "Something went wrong!", "error": str(e), "data": None}, 500


@app.route("/users", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({"message": "successfully retrieved user profile", "data": current_user})


@app.route("/users", methods=["PUT"])
@token_required
def update_user(current_user):
    try:
        user = request.json
        if user.get("first_name"):
            user = User().update(current_user["_id"], **user)
            return jsonify({"message": "successfully updated account", "data": user}), 201
        return {
            "message": "Invalid data, you can only update your account name!",
            "data": None,
            "error": "Bad Request",
        }, 400
    except Exception as e:
        return jsonify({"message": "failed to update account", "error": str(e), "data": None}), 400


@app.route("/users", methods=["DELETE"])
@token_required
def disable_user(current_user):
    try:
        User().disable_account(current_user["_id"])
        return jsonify({"message": "successfully disabled acount", "data": None}), 204
    except Exception as e:
        return jsonify({"message": "failed to disable account", "error": str(e), "data": None}), 400


@app.route("/template", methods=["POST"])
@token_required
def add_template(current_user):
    try:
        template = dict(request.json)
        if not template:
            return {
                "message": "Invalid data, you need to give the template title, cover image, author id,",
                "data": None,
                "error": "Bad Request",
            }, 400

        template["user_id"] = current_user["_id"]
        template = Templates().create(**template)
        if not template:
            return {
                "message": "The template has been created by another user",
                "data": None,
                "error": "Conflict",
            }, 400
        return jsonify({"message": "successfully created a new template", "data": template}), 201
    except Exception as e:
        return (
            jsonify({"message": "failed to create a new template", "error": str(e), "data": None}),
            500,
        )


@app.route("/template", methods=["GET"])
@token_required
def get_templates(current_user):
    try:
        templates = Templates().get_by_user_id(current_user["_id"])
        return jsonify({"message": "successfully retrieved all templates", "data": templates})
    except Exception as e:
        return (
            jsonify({"message": "failed to retrieve all templates", "error": str(e), "data": None}),
            500,
        )


@app.route("/template/<template_id>", methods=["GET"])
@token_required
def get_template(current_user, template_id):
    try:
        template = Templates().get_by_id(template_id)
        if not template:
            return {"message": "Book not found", "data": None, "error": "Not Found"}, 404
        return jsonify({"message": "successfully retrieved a template", "data": template})
    except Exception as e:
        return jsonify({"message": "Something went wrong", "error": str(e), "data": None}), 500


@app.route("/template/<template_id>", methods=["PUT"])
@token_required
def update_template(current_user, template_id):
    try:
        template = Templates().get_by_id(template_id)
        if not template or template["user_id"] != current_user["_id"]:
            return {
                "message": "Template not found for user",
                "data": None,
                "error": "Not found",
            }, 404
        template = request.json
        template = Templates().update(template_id, **template)
        return jsonify({"message": "successfully updated a template", "data": template}), 201
    except Exception as e:
        return (
            jsonify({"message": "failed to update a template", "error": str(e), "data": None}),
            400,
        )


@app.route("/template/<template_id>", methods=["DELETE"])
@token_required
def delete_template(current_user, template_id):
    try:
        template = Templates().get_by_id(template_id)
        if not template or template["user_id"] != current_user["_id"]:
            return {
                "message": "Template not found for user",
                "data": None,
                "error": "Not found",
            }, 404
        Templates().delete(template_id)
        return jsonify({"message": "successfully deleted a template", "data": None}), 204
    except Exception as e:
        return (
            jsonify({"message": "failed to delete a template", "error": str(e), "data": None}),
            400,
        )


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"message": "Forbidden", "error": str(e), "data": None}), 403


@app.errorhandler(404)
def forbidden(e):
    return jsonify({"message": "Endpoint Not Found", "error": str(e), "data": None}), 404


if __name__ == "__main__":
    app.run(debug=True)
