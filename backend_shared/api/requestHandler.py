from backend_shared.database import db_connection, db_utils, db_executer
from backend_shared.security import verifier, token, crypt
from backend_shared.logger import logger
from backend_shared.utils import random
from backend_shared.types import BusinessResponse, BusinessError, Role
from backend_shared.connector import mail_connector
from flask import  make_response
import requests

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
        self.mail_connector = mail_connector.MailConnector(self.config)
        self.crypto = crypt.Encrpyter(self.config)

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
        if self.config["account_service"]["verify_email"]:
            if not account[0][10]: BusinessResponse(self.random.CreateRandomId(), "login-failed", []).toJson()
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
        try: username, password, email , re_password= request.json["username"], request.json["password"], request.json["email"], request.json["re_password"]
        except: return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", []).toJson()
        if password != re_password: return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()
        username = self.random.CreateMD5Hash(self.verifier.escape_characters(username))
        password = self.verifier.escape_characters(password)
        if self.verifier.verify_account(username, password): return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", [], BusinessError(self.random.CreateRandomId(), "can not create user")).toJson()

        if self.config["account_service"]["rsa_enabled"]: email = self.crypto.enc_private_key(self.verifier.escape_characters(email)).hex()
        else: email = self.verifier.escape_characters(email)
        salt, verifier = self.verifier.get_registrationData(username, password)
        id = self.random.CreateRandomId()
        self.db_executer.create_account(id, username, username, verifier, salt, email, self.config["roles"]["user"], "default")
        if not self.verifier.verify_account(username, password): return BusinessResponse(self.random.CreateRandomId(), "error creating user", [], BusinessError(self.random.CreateRandomId(), "can not create user"))
        self.logger.log("INFO", f"{self.config['roles']['user']} user created")
        try:
            if self.config["account_service"]["verify_email"]:
                code = self.random.CreateRandomId()
                self.db_executer.create_verification_code(id, code) 
                self.mail_connector.send_verification_email(id, code, self.verifier.escape_characters(request.json["email"]))
        except: return BusinessResponse(self.random.CreateRandomId(), f"error creating {self.config['roles']['user']}", []).toJson()
        return BusinessResponse(self.random.CreateRandomId(), "account-created", [self.config["account_service"]["verify_email"]]).toJson()

    def verify_account(self, request):
        try: id = self.verifier.escape_characters(request.args.get("id"))
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), "error verify account", []).toJson()
        try: code = self.verifier.escape_characters(request.args.get("code"))
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), "error verify account", []).toJson()
        try:result = self.db_executer.get_verification_entry(id, code)
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), "error verify account", []).toJson()
        try: id = result[0][0]
        except Exception as e: 
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), "error verify account", []).toJson()
        try: self.db_executer.verify_account(id)
        except Exception as e: 
            self.logger.log("ERROR", str(e))
        try: self.db_executer.update_account_verification(id)
        except Exception as e:
            self.logger.log("ERROR", str(e))
            return BusinessResponse(self.random.CreateRandomId(), "error verify account", []).toJson()
        self.logger.log("INFO", f"Account: {id} verified with code: {code}")
        return BusinessResponse(self.random.CreateRandomId(), "account-verified", []).toJson()

