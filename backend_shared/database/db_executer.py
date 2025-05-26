import datetime, re

class Executer:
    def __init__(self, connection, config):
        self.connection = connection
        self.config = config

    def create_account(self, id, username, nickname, verifier, salt, email, role, sub_role=""):
        rc, result = self.connection.execute(f'''insert into {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} (
                                id,
                                username, 
                                nickname,             
                                verifier, 
                                salt, 
                                email_address, 
                                role, 
                                sub_role,
                                datetime) 
                                values (
                                '{id}',
                                '{username}', 
                                '{nickname}', 
                                X'{verifier}', 
                                X'{salt}', 
                                '{email}',
                                '{role}',
                                '{sub_role}',
                                '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}')''')
        return result
    
    def delete_account(self, id):
        self.connection.execute(f"delete from {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} where id = {id}")

    def get_account_by_username(self, username):
        q = f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"'''
        print(f"get account query => {q}")
        rc, result = self.connection.execute(f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"''')
        return result
    
    def get_account_by_id(self, id):
        rc, result = self.connection.execute(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} where id = '{id}'")
        return result
    
    def get_verification_entry(self, id, code):
        rc, result = self.connection.execute(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][1]['name']} where id = '{id}' and code = '{code}' and soft_delete = 0")
        return result
    
    def verify_account(self, id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][0]["name"]} set verified = '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}' where id = "{id}"''')

    def update_account_verification(self, id):
        rc, result = self.connection.execute(f'''update {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} set verified_at = '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}', soft_delete = 1 where id = "{id}"''')

    def create_verification_code(self, id, code):
        rc, result = self.connection.execute(f'''insert into {self.config["database"]["name"]}.{self.config["database"]["tables"][1]["name"]} (id, code, created_at) values ('{id}', '{code}', '{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}')''')