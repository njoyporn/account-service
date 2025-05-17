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
        pass

    def get_account_by_username(self, username):
        q = f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"'''
        print(f"get account query => {q}")
        rc, result = self.connection.execute(f'''select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} 
                                             where username = "{username}"''')
        return result
    
    def get_account_by_id(self, id):
        rc, result = self.connection.execute(f"select * from {self.config['database']['name']}.{self.config['database']['tables'][0]['name']} where id = {id}")
        return result