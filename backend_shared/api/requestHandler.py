from backend_shared.database import db_connection, db_utils, db_executer
from backend_shared.security import verifier, token
from backend_shared.logger import logger
from backend_shared.utils import random
from backend_shared.types import BusinessResponse, BusinessError, Role
from flask import  make_response

class RequestHandler:
    def __init__(self, config):
        self.config = config
        self.db_connection = db_connection.Connection(self.config["database"]["hostname"], self.config["database"]["user"]["username"], self.config["database"]["user"]["password"], self.config["database"]["name"], self.config["database"]["port"])
        self.verifier = verifier.Verifier(self.db_connection, self.config)
        self.db_executer = db_executer.Executer(self.db_connection, self.config)
        self.db_utils = db_utils.DBUtils()
        self.logger = logger.Logger()
        self.random = random.Random()
        self.tokenizer = token.Tokenizer(self.config)

    def handle_login(self, request):
        try:
            username = self.random.CreateMD5Hash(self.verifier.escape_characters(request.json["username"]))
            password = self.verifier.escape_characters(request.json["password"])
        except:pass
        try:
            username = self.random.CreateMD5Hash(self.verifier.escape_characters(request.form["username"]))
            password = self.verifier.escape_characters(request.form["password"])
        except:pass
        if not self.verifier.verify_account(username, password):
            self.logger.log("INFO", f"Denaied login with username: {username}")
            return BusinessResponse(self.random.CreateRandomId(), "login-failed", []).toJson()
        account = self.db_executer.get_account_by_username(username)

        self.tokenizer.create_token({'id':account[0][0], 'role':account[0][6]})
        self.logger.log("INFO", f"Success login with username: {username}")
        response = make_response(BusinessResponse(self.random.CreateRandomId(), "login-success", [], None, self.tokenizer.create_token({'id':account[0][0], 'role':account[0][6]})).toJson())
        response.headers["Authorization"] = f"Bearer {self.tokenizer.create_token({'id':account[0][0], 'role':account[0][6]})}"
        return response

    def handle_check_is_logged_in(self, request):
        try: 
            userData = self.tokenizer.decode(request.headers["Authorization"])
            response = make_response(BusinessResponse(self.random.CreateRandomId(), "authorized", [Role(userData['role'])]).toJson())
            response.headers["Authorization"] = request.headers.get("Authorization")
            return response
        except Exception as e: 
            self.logger.log("ERROR", f"cant handle check is loged in... {str(e)}")
            return BusinessResponse(self.random.CreateRandomId(), "not-authorized", []).toJson()

    def handle_log_out(self, request):
        return "200 OK" 

    def register_account(self, request):
        if not self.config["account_service"]["allow_account_creation"]: return BusinessResponse(self.random.CreateRandomId(), "error creating user", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()
        try: username, password, email = request.json["username"], request.json["password"], request.json["email"]
        except: return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", []).toJson()
        username = self.random.CreateMD5Hash(self.verifier.escape_characters(username))
        password = self.verifier.escape_characters(password)
        if self.verifier.verify_account(username, password): return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()
        if self.config["account_service"]["rsa_enabled"]: email = self.crypto.enc_private_key(self.verifier.escape_characters(email)).hex()
        else: email = self.verifier.escape_characters(email)
        salt, verifier = self.verifier.get_registrationData(username, password)
        self.db_executer.create_account(self.random.CreateRandomId(), username, username, verifier, salt, email, self.config["roles"]["user"], "default")
        if not self.verifier.verify_account(username, password): return BusinessResponse(self.random.CreateRandomId(), "error creating user", [], BusinessError(self.random.CreateRandomId(), "can not create user"))
        self.logger.log("INFO", f"{self.config['roles']['user']} user created")
        return BusinessResponse(self.random.CreateRandomId(), "account-created", []).toJson()