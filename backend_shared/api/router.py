from flask import Flask, request
from .requestHandler import RequestHandler
import os

api = Flask(__name__)

request_handler = None

base_route = "/api/v1"
data_path = f"{os.getcwd()}/binarys"

@api.route("/", methods=["GET"])
def index():
    return "200 OK from account-service"

@api.route(f"{base_route}/healthz", methods=["GET"])
def healthz():
    return "200 OK from account-service"

@api.route(f"{base_route}/login", methods=["POST"])
def login():
    return request_handler.handle_login(request)

@api.route(f"{base_route}/login", methods=["GET"])
def check_is_logged_in():
    return request_handler.handle_check_is_logged_in(request)

@api.route(f"{base_route}/logout", methods=["GET"])
def log_out():
    return request_handler.handle_log_out(request)

@api.route(f"{base_route}/register", methods=["POST"])
def register_account():
    return request_handler.register_account(request)

def run(conf):
    global config, request_handler
    config = conf
    request_handler = RequestHandler(config)
    if config["account_service"]["cors_enabled"]:
        from flask_cors import CORS
        cors = CORS(api)
    api.run(debug=True, host=config["account_service"]["hostname"], port=config["account_service"]["port"])
