import mysql.connector
import json

class Connection:
    is_config = False
    def load_config(self,):
        try:
            with open("./config.json", "r") as config:
                config_data = json.load(config)
        except:
            print("Error: cannot open config.json file.")
            return
        try:
            self.user = config_data["user"]
            self.password = config_data["password"]
            self.host = config_data["host"]
            self.database = config_data["database"]
        except:
            print("Error: missing key/value in config.json file.")
            return
        self.is_config = True
        print("Config file load succeed.")

    def write_config(self,user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        config_data = { "user":user, "password":password, "host":host, "database":database}
        with open('config.json', 'w') as config:
            json.dump(config_data, config, indent=4)

    # return MySQLConnection object
    def start_connection(self,):
        self.load_config()
        self.cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
        print("Start connection succeed.")
    
    def get_cube():
        pass

    def __init__(self):
        pass
        
connect = Connection()
connect.start_connection()