import mysql.connector as database
import random
import string
from datetime import datetime
from mega_data import mega_data


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
        self.valid_duration = 300

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
        self.show_table()
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
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
            if qr_code in record[0][0] and datetime.now().timestamp() - int(float(record[0][2])) < self.valid_duration:
                print(f"valid QR code '{qr_code}'")
                self.delete_qr_code(qr_code)

                mega_id, position = self.get_meag_id_position(record[0][1])
                position = str(position)
                while len(position) < 2:
                    position = "0" + position
                position = "L" + position
                return True, record[0][1], mega_id, position
            else:
                print(f"expired QR code '{qr_code}'.")
                self.delete_qr_code(qr_code)
                return False, "", "", ""
        else:
            print(f"invalid QR code '{qr_code}'.")
            return False, "", "", ""

    def check_duplicated_qr(self, qr_code):
        self.cursor.execute(f"SELECT qr_code FROM qr_code")
        record = [x[0] for x in self.cursor]
        if qr_code in record: return True
        else: return False

    def generate_qr_code(self):
        is_duplicate = True
        random_letters = ""
        while is_duplicate:
            letters = string.ascii_lowercase
            random_letters = ''.join(random.choice(letters) for _ in range(25))
            is_duplicate = self.check_duplicated_qr(random_letters)
        current_time = datetime.now().timestamp()
        return random_letters, current_time

    def insert_qr_code(self, flat):
        random_letters, current_time = self.generate_qr_code()
        sql = "INSERT INTO qr_code (qr_code, flat, time) VALUES (%s, %s, %s)"
        val = (random_letters, flat.upper(), current_time)
        self.cursor.execute(sql, val)
        self.connection.commit()
        return random_letters

    def refresh_qr_code(self, flat):
        new_qr_code, time = self.generate_qr_code()

        sql = f"SELECT 1 FROM qr_code WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        record = [x for x in self.cursor]
        if len(record) != 0:
            sql = f"UPDATE qr_code SET qr_code = '{new_qr_code}', time = '{time}' WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        else:
            new_qr_code = self.insert_qr_code(flat)

        sql = f"UPDATE qr_code SET qr_code = '{new_qr_code}', time = '{time}' WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        return new_qr_code

    def check_if_still_valid(self, table, flat):
        sql = f"SELECT {table}, time FROM {table} WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        record = [x for x in self.cursor]
        if len(record) != 0:
            if int(float(record[0][1])) + self.valid_duration > datetime.now().timestamp():
                return record[0][0], True, float(record[0][1])
            else:
                sql = f"DELETE FROM {table} WHERE flat = '{flat}'"
                self.cursor.execute(sql)
                return "", False, record[0][1]
        else:
            time = datetime.now().timestamp()
            if table == "qr_code":
                qr = self.insert_qr_code(flat)
                return qr, True, time
            elif table == "pin":
                p = self.insert_pin(flat)
                return p, True, time

    def delete_pin(self, pin):
        self.cursor.execute(f"DELETE FROM pin WHERE pin = '{pin}'")
        self.connection.commit()

    def check_pin(self, pin):
        self.cursor.execute(f"SELECT * FROM pin WHERE pin = '{pin}'")
        record = [x for x in self.cursor]
        if len(record) != 0:
            if pin in record[0][0] and datetime.now().timestamp() - int(float(record[0][2])) < self.valid_duration:
                self.delete_pin(pin)

                mega_id, position = self.get_meag_id_position(record[0][1])
                position = str(position)
                while len(position) < 2:
                    position = "0" + position
                position = "L" + position

                return True, record[0][1], mega_id, position
            else:
                self.delete_pin(pin)
                return False, "", "", ""
        else:
            return False, "", "", ""

    def check_duplicated_pin(self, pin):
        self.cursor.execute(f"SELECT pin FROM pin")
        record = [x[0] for x in self.cursor]
        if pin in record:
            return True
        else:
            return False

    def insert_pin(self, flat):
        random_digit, current_time = self.generate_pin_code()
        sql = "INSERT INTO pin (pin, flat, time) VALUES (%s, %s, %s)"
        val = (random_digit, flat.upper(), current_time)
        self.cursor.execute(sql, val)
        self.connection.commit()
        return random_digit

    def check_rfid(self, unique_id):
        self.cursor.execute(f"SELECT * FROM rfid WHERE id = '{unique_id}'")
        record = [x for x in self.cursor]
        if len(record) != 0:
            if unique_id in record[0][0]:

                mega_id, position = self.get_meag_id_position(record[0][1])
                position = str(position)
                while len(position) < 2:
                    position = "0" + position
                position = "L" + position

                return True, record[0][1], mega_id, position
        else:
            return False, "", "", ""

    def insert_rfid(self, card, flat):
        sql = "INSERT INTO rfid (id, flat) VALUES (%s, %s)"
        val = (card, flat)
        self.cursor.execute(sql, val)
        self.connection.commit()

    def init_data(self):
        # self.create_database("mailbox")  // run this after creating the tables for new database set up
        for n in range(10):
            self.insert_pin("1A")
            self.insert_qr_code('1B')
        self.insert_rfid("148037121234", "1A")
        self.insert_rfid("315569001347", "1B")
        self.insert_data("1B", 0, 0, 0, 0, "closed", "closed")
        self.show_all_data()

    def show_all_data(self):
        self.show_data("rfid")
        self.show_data("qr_code")
        self.show_data("pin")

    def insert_data(self, flat, new_letter, door_alert, letter_alert, tof_alert, door_status, lock_status):
        sql = "INSERT INTO data (flat, new_letter, door_alert, letter_alert, tof_alert, door_status, lock_status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (flat, new_letter, door_alert, letter_alert, tof_alert, door_status, lock_status)
        self.cursor.execute(sql, val)
        self.connection.commit()

    def get_mailbox_data(self, flat):
        sql = f"SELECT * FROM data WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        record = [x for x in self.cursor]
        if len(record) != 0:
            data = {
                "receiver": record[0][0],
                "new_letter": record[0][1],
                "door_alert": record[0][2],
                "letter_alert": record[0][3],
                "tof_alert": record[0][4],
                "door_status": record[0][5],
                "lock_status": record[0][6]
            }
            return data
        else:
            return ""

    def get_qr_code(self, flat):
        qr_code = self.insert_qr_code(flat)
        return qr_code

    def get_pin(self, flat):
        pin = self.insert_pin(flat)
        return pin

    def reset_qr_code_table(self):
        self.delete_table("qr_code")
        qr_table = "CREATE TABLE qr_code (qr_code VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"
        self.cursor.execute(qr_table)
        self.insert_qr_code("1A")
        self.insert_qr_code("1B")
        self.show_data("qr_code")

    def reset_pin_table(self):
        self.delete_table("pin")
        pin_table = "CREATE TABLE pin (pin VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"
        self.cursor.execute(pin_table)
        self.insert_pin("1A")
        self.insert_pin("1B")
        self.show_data("pin")

    def refresh_pin_code(self, flat):
        new_pin_code, time = self.generate_pin_code()
        sql = f"SELECT 1 FROM pin WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        record = [x for x in self.cursor]
        if len(record) != 0:
            sql = f"UPDATE pin SET pin = '{new_pin_code}', time = '{time}' WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        else:
            new_pin_code = self.insert_pin(flat)
        return new_pin_code

    def generate_pin_code(self):
        is_duplicate = True
        random_letters = ""
        while is_duplicate:
            letters = string.digits
            random_letters = ''.join(random.choice(letters) for _ in range(6))
            is_duplicate = self.check_duplicated_pin(random_letters)
        current_time = datetime.now().timestamp()
        return random_letters, current_time

    def reset_alert(self, flat):
        sql = f"UPDATE data SET door_alert = 0, tof_alert = 0, letter_alert = 0 WHERE flat = '{flat}'"
        self.cursor.execute(sql)

    def update_data_from_arduino(self, flat, detection):
        if detection == "letter_alert":
            sql = f"UPDATE data SET letter_alert = letter_alert + 1 WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "tof_alert":
            sql = f"UPDATE data SET tof_alert = tof_alert + 1 WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "door_alert":
            sql = f"UPDATE data SET door_alert = door_alert + 1, door_status = 'open' WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "new_letter":
            sql = f"UPDATE data SET new_letter = new_letter + 1 WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "lock_open":
            sql = f"UPDATE data SET lock_status = 'open', door_status = 'open', new_letter = 0 WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "lock_close":
            sql = f"UPDATE data SET lock_status = 'close', door_status = 'close' WHERE flat = '{flat}'"
            self.cursor.execute(sql)
        elif detection == "door_closed":
            sql = f"UPDATE data SET door_status = 'close' WHERE flat = '{flat}'"
            self.cursor.execute(sql)

    def is_data_in_db(self, table, flat):
        sql = f"SELECT {table}, time FROM {table} WHERE flat = '{flat}'"
        self.cursor.execute(sql)
        record = [x for x in self.cursor]
        if len(record) != 0:
            if int(float(record[0][1])) + self.valid_duration > datetime.now().timestamp():
                return True
            else:
                return False
        else:
            return False

    def get_meag_id_position(self, flat):
        for key, value in mega_data.items():
            if flat in value:
                return key, value.index(flat)
            else:
                return "", ""

"""
    "SELECT * FROM customers"
    "SELECT * FROM rfid WHERE flat = '1A'"

    sql = "INSERT INTO rfid (id, flat) VALUES (%s, %s)"
    val = ("315569001347", "1B")
    test.cursor.execute(sql, val)
    test.connection.commit()
    

# create table

rfid_table = "CREATE TABLE rfid (id VARCHAR(255) PRIMARY KEY, flat VARCHAR(255))"  
    
qr_table = "CREATE TABLE qr_code (qr_code VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"
    
pin_table = "CREATE TABLE pin (pin VARCHAR(255) PRIMARY KEY, flat VARCHAR(255), time VARCHAR(255))"

data_table = "CREATE TABLE data (flat VARCHAR(255) PRIMARY KEY, new_letter INT, door_alert INT, letter_alert INT, tof_alert INT, door_status VARCHAR(255), lock_status VARCHAR(255))"
    
"""



# test = MySQL("mailbox")
# # # test.insert_pin("1A")
# test.show_all_data()
