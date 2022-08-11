"""Validator Module"""
import re

from bson.objectid import ObjectId


def validate(data, regex):
    """Custom Validator"""
    return True if re.match(regex, data) else False


def validate_password(password: str):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return validate(password, reg)


def validate_email(email: str):
    """Email Validator"""
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return validate(email, regex)


def validate_template(**args):
    """Book Validator"""
    if (
        not args.get("template_name")
        or not args.get("subject")
        or not args.get("body")
        or not args.get("user_id")
    ):
        return {
            "template_name": "Template name is required",
            "subject": "Subject is required",
            "body": "Body is required",
            "user_id": "User ID is required",
        }

    try:
        ObjectId(args.get("user_id"))
    except:
        return {"user_id": "User ID must be valid"}
    if (
        not isinstance(args.get("template_name"), str)
        or not isinstance(args.get("body"), str)
        or not isinstance(args.get("subject"), str)
    ):
        return {
            "template_name": "Template must be a string",
            "subject": "Subject must be a string",
            "body": "Body must be a string",
        }
    return True


def validate_user(**args):
    """User Validator"""
    if (
        not args.get("email")
        or not args.get("password")
        or not args.get("first_name")
        or not not args.get("last_name")
    ):
        return {
            "email": "Email is required",
            "password": "Password is required",
            "first_name": "First name is required",
            "last_name": "Last name is required",
        }
    if (
        not isinstance(args.get("first_name"), str)
        or not isinstance(args.get("first_name"), str)
        or not isinstance(args.get("email"), str)
        or not isinstance(args.get("password"), str)
    ):
        return {
            "email": "Email must be a string",
            "password": "Password must be a string",
            "first name": "First name must be a string",
            "last name": "Last name must be a string",
        }
    if not validate_email(args.get("email")):
        return {"email": "Email is invalid"}
    if not validate_password(args.get("password")):
        return {
            "password": "Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters"
        }
    if not 2 <= len(args["name"].split(" ")) <= 30:
        return {"name": "Name must be between 2 and 30 words"}
    return True


def validate_email_and_password(email, password):
    """Email and Password Validator"""
    if not (email and password):
        return {"email": "Email is required", "password": "Password is required"}
    if not validate_email(email):
        return {"email": "Email is invalid"}
    if not validate_password(password):
        return {
            "password": "Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters"
        }
    return True
