import mysql.connector as database
import random
import string
from datetime import datetime


class MySQL:

    def __init__(self, db=""):
        self.db = db
        self.connection = database.connect(
            user="root",
            password="python_mysql",
            host="localhost",
            database=self.db
        )
        self.cursor = self.connection.cursor()

    def create_database(self, db_name):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    def show_database(self):
        self.cursor.execute("SHOW DATABASES")
        for x in self.cursor: print(x)

    def show_table(self):
        self.cursor.execute("SHOW TABLES")
        for x in self.cursor: print(x)

    def show_data(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        record = [x for x in self.cursor]
        for x in record: print(x)
        print(f"record found: {len(record)}")

    def delete_table(self, table_name):
        print("Before")
        self.show_table()
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print("After")
        self.show_table()

    def delete_database(self, db_name):
        self.cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print("current database:")
        self.show_database()

    def delete_qr_code(self, qr_code):
        self.cursor.execute(f"DELETE FROM qr_code WHERE qr_code = '{qr_code}'")
        self.connection.commit()

    def check_qr_code(self, qr_code):
        self.cursor.execute(f"SELECT * FROM qr_code WHERE qr_code = '{qr_code}'")
        record = [x for x in self.cursor]
        if len(record) != 0:
            if qr_code in record[0][0] and datetime.now().timestamp() - int(float(record[0][2])) < 60:
                print(f"valid QR code '{qr_code}'")
                self.delete_qr_code(qr_code)
                return True, record[0][1]
            else:
                print(f"expired QR code '{qr_code}'.")
                self.delete_qr_code(qr_code)
                return False, ""
        else:
            print(f"invalid QR code '{qr_code}'.")
            return False, ""

    def check_duplicated_qr(self, qr_code):
        self.cursor.execute(f"SELECT qr_code FROM qr_code")
        record = [x[0] for x in self.cursor]
        if qr_code in record: return True
        else: return False

    def insert_qr_code(self, flat):
        is_duplicate = True
        random_letters = ""
        while is_duplicate:
            letters = string.ascii_lowercase
            random_letters = ''.join(random.choice(letters) for _ in range(25))
            is_duplicate = self.check_duplicated_qr(random_letters)
        current_time = datetime.now().timestamp()
        sql = "INSERT INTO qr_code (qr_code, flat, time) VALUES (%s, %s, %s)"
        val = (random_letters, flat.upper(), current_time)
        self.cursor.execute(sql, val)
        self.connection.commit()
        return random_letters

    def delete_pin(self, pin):
        self.cursor.execute(f"DELETE FROM pin WHERE pin = '{pin}'")
        self.connection.commit()

    def check_pin(self, pin):
        self.cursor.execute(f"SELECT * FROM pin WHERE pin = '{pin}'")
        record = [x for x in self.cursor]
        if len(record) != 0:
            if pin in record[0][0] and datetime.now().timestamp() - int(float(record[0][2])) < 60:
                print(f"valid Pin '{pin}'")
                self.delete_pin(pin)
                return True, record[0][1]
            else:
                print(f"expired Pin '{pin}'.")
                self.delete_pin(pin)
                return False, ""
        else:
            print(f"invalid Pin '{pin}'.")
            return False, ""

    def check_duplicated_pin(self, pin):
        self.cursor.execute(f"SELECT pin FROM pin")
        record = [x[0] for x in self.cursor]
        if pin in record:
            return True
        else:
            return False

    def insert_pin(self, flat):
        is_duplicate = True
        random_digit = ""
        while is_duplicate:
            digits = string.digits
            random_digit = ''.join(random.choice(digits) for _ in range(6))
            is_duplicate = self.check_duplicated_pin(random_digit)
        current_time = datetime.now().timestamp()
        sql = "INSERT INTO pin (pin, flat, time) VALUES (%s, %s, %s)"
        val = (random_digit, flat.upper(), current_time)
        self.cursor.execute(sql, val)
        self.connection.commit()
        return random_digit

    def check_rfid(self, unique_id):
        self.cursor.execute(f"SELECT * FROM rfid WHERE id = '{unique_id}'")
        record = [x for x in self.cursor]
        print(f"checking rfid card: '{unique_id}'")
        print(record)
        if len(record) != 0:
            if unique_id in record[0][0]:
                print(f"valid card '{unique_id}'")
                return True, record[0][1]
        else:
            print(f"invalid card '{unique_id}'")
            return False, ""

    def insert_rfid(self, card, flat):
        sql = "INSERT INTO rfid (id, flat) VALUES (%s, %s)"
        val = (card, flat)
        self.cursor.execute(sql, val)
        self.connection.commit()

    def init_data(self):
        # self.create_database("mailbox")
        for n in range(10):
            self.insert_pin("1A")
            self.insert_qr_code('1B')
        self.insert_rfid("148037121234", "1A")
        self.insert_rfid("315569001347", "1B")
        self.show_data("rfid")
        self.show_data("qr_code")
        self.show_data("pin")

# TODO CREATE TABLE
#     "CREATE TABLE rfid (id VARCHAR(255) PRIMARY KEY, flat VARCHAR(255))"
#     "CREATE TABLE qr_code (qr_code VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"
#     "CREATE TABLE pin (pin VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"

# TODO SELECT
#     "SELECT * FROM customers"
#     "SELECT * FROM rfid WHERE flat = '1A'"

# TODO INSERT
#     sql = "INSERT INTO rfid (id, flat) VALUES (%s, %s)"
#     val = ("315569001347", "1B")
#     test.cursor.execute(sql, val)
#     test.connection.commit()


# create_table = [
#     "CREATE TABLE rfid (id VARCHAR(255) PRIMARY KEY, flat VARCHAR(255))",
#     "CREATE TABLE qr_code (qr_code VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))",
#     "CREATE TABLE pin (pin VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"
# ]
#
# test = MySQL("mailbox")
# test.show_data("rfid")
# test.show_data("qr_code")
# test.show_data("pin")
