import os
import mysql.connector


class DataBase:
    """Provides a database object.
    """

    def __init__(self, exchanges, pair, db_name, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.create_database()
        # Creates a table for storing price & spread
        table_col = f'{pair} (Exchange VARCHAR(23), Price_USD FLOAT, Spread FLOAT,' \
            ' Time TIME, Date VARCHAR(23), Duration FLOAT)'
        self.create_table(table_col)
        # Creates a table for storing trade history
        for exc in exchanges:
            table_col = f'{exc.name} (Amount FLOAT, Price FLOAT,' \
                ' Time VARCHAR(23), Date VARCHAR(23))'
            self.create_table(table_col)
        print('Database connection is successfully established!')

    def connect(self):
        """Connects to SmySQL database

        Args:
            db_name (str): database name

        Returns:
            obj: connection obj
        """
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            return self.conn
        except mysql.connector.Error as Err:
            print(Err)

    def create_table(self, col):
        """Creates an SQL table.

        Args:
            col (str): table columns acc. to mySQL query
            db_name (str): database name
        """
        try:
            cursor = self.connect().cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {col}')
            cursor.close()
        except mysql.connector.Error as Err:
            print(Err)

    def create_database(self):
        """Creates a SQL database

        Args:
            db_name (str): database name
        """
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user=os.environ.get('MYSQL_USER'),
                password=os.environ.get('MYSQL_PASS'),
            )
            conn.cursor().execute(
                f'CREATE DATABASE IF NOT EXISTS {self.db_name}')
        except mysql.connector.Error as Err:
            print(Err)

    def upload_price_spread(self, sql):
        """Uploads price % spread data to SQL database

        Args:
            sql (str): sql query
        """
        mydb = self.connect()
        mydb.cursor().execute(sql)
        mydb.commit()
        mydb.cursor().close()

    def upload_trade_hist(self, sql, data):
        """Uploads trade history data to SQL database

        Args:
            sql (str): sql query
            data (list): trade history data
        """
        mydb = self.connect()
        mydb.cursor().executemany(sql, data)
        mydb.commit()
        mydb.cursor().close()
