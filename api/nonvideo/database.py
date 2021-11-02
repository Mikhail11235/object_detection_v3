import MySQLdb


INT_DATA_TYPE = 1
STR_DATA_TYPE = 2
BOOL_DATA_TYPE = 3


class DB:
    TABLES = ["users", "user_password"]
    TABLE_FIELDS = {"users": {"user_id": INT_DATA_TYPE,
                              "firstname": STR_DATA_TYPE,
                              "lastname": STR_DATA_TYPE,
                              "premium": BOOL_DATA_TYPE},
                    "user_password": {"user_id": INT_DATA_TYPE,
                                      "password": STR_DATA_TYPE}}

    def __init__(self):
        self.db_connection = MySQLdb.connect(host='0.0.0.0', user='root', passwd='123456', db='ovd', port=3306)
        self.cursor = self.db_connection.cursor()

    def insert(self, table, values):
        if table not in self.TABLES:
            print("Error: Invalid table name: %s" % table)
            return False
        insert_fields = []
        insert_values = []
        for key, val in values.items():
            if key not in self.TABLE_FIELDS[table].keys():
                print("Error: Invalid field name: %s" % key)
                return False
            else:
                if self.TABLE_FIELDS[table][key] in (INT_DATA_TYPE, BOOL_DATA_TYPE):
                    insert_values.append("%d" % val)
                else:
                    insert_values.append("\'%s\'" % val)
            insert_fields.append(key)
        insert_fields = ", ".join(insert_fields)
        insert_values = ", ".join(insert_values)
        self.cursor.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, insert_fields, insert_values))
        self.db_connection.commit()
        return self.cursor.lastrowid

    def load(self):
        pass

    def delete(self, table, record):
        if table not in self.TABLES:
            print("Error: Invalid table name: %s" % table)
            return False
        id_field = self.TABLES[table].keys()[0]
        self.cursor.execute("DELETE FROM %s WHERE %s = %d" % (table, id_field, record))
        return True
