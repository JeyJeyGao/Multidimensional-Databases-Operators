import mysql.connector
from mysql.connector import errorcode
import json

class Backend:
    is_config = False
    is_connected = False
    def load_config(self,):
        try:
            with open("./config.json", "r") as config:
                config_data = json.load(config)
        except:
            print("Error: cannot open config.json file.")
            return False
        try:
            self.user = config_data["user"]
            self.password = config_data["password"]
            self.host = config_data["host"]
            self.database = config_data["database"]
        except:
            print("Error: missing key/value in config.json file.")
            return False
        self.is_config = True
        print("Config file load succeed.")
        return True

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
        if self.load_config() == False:
            return
        try:
            self.cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
                return
        else:
            self.is_connected = True
            print("Start connection succeed.")
    
    def get_table(self, table_name):
        if self.is_connected == False:
            print("Backend is not connected.")
            return
        cursor = self.cnx.cursor()
        # get rows data
        rows = []
        query_rows = ("SELECT * FROM {}".format(table_name))
        cursor.execute(query_rows)
        for row in cursor:
            rows.append(row)
        # get dimentions name
        dimentions_info = [] # full dimention info from database
        dimentions_name = [] # only dimention name
        query_dimention_name = ("SELECT * FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{}'".format(table_name))
        cursor.execute(query_dimention_name)
        for dimention in cursor:
            dimentions_info.append(dimention)
            dimentions_name.append(dimention[3])
        return (dimentions_name, rows)

        
        
    def get_cube():
        pass

    def __init__(self):
        pass
        
connect = Backend()
connect.start_connection()
connect.get_table("Product")