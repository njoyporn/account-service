import requests
import os, re, json as JSON
from backend_shared.logger import logger

class MailConnector():
    def __init__(self, config):
        self.config = config
        self.logger = logger.Logger()

    def load_template(self, filename):
        with open(f"{os.getcwd()}/{self.config['data']['path']}/mail_templates/{filename}", "r", encoding="utf-8") as fd:
            return JSON.load(fd)

    def send_verification_email(self, id, code, email):
        try:
            template = self.load_template('verification.json')
            template["Content"] = self.set_id(template["Content"], id)
            template["Content"] = self.set_code(template["Content"], code)
            template["To"] = email
            requests.post(f"{self.config['connectors']['email']['host']}:{self.config['connectors']['email']['port']}/api/v1/send-mail", json=template)
            self.logger.log("INFO", f"Send verification-email to user with id: {id}")
        except Exception as e: self.logger.log("ERROR", f"Can't send verification email || error => {e}")

    def set_id(self, content, id):
        return re.sub('{{ID}}', id, content)
    def set_code(self, content, code):
        return re.sub('{{CODE}}', code, content)
