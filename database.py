class DBManager:

    """
        for using an instance of this class you should
        set the db_name
        set the set_queries to your table name to change the queries as needed
        then you can use the right method
    """

    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = DataExtraction()
        return cls.instance
    
    def __init__(self, db_name):
        self.db_name = db_name


    def set_queries(self, table_name):
        self._table_query = f"CREATE TABLE {table_name} (`model` varchar(30), `usage` int(15), `city` varchar(15), `year` int(4), `price` bigint(20))"
        
        self._insert_query = f"INSERT INTO {table_name} (`model`, `usage`, `city`, `year`, `price`) VALUES(%s, %s, %s, %s, %s)"
        
        self._temp_query = [f'CREATE TABLE temp LIKE {table_name}', f'INSERT INTO temp SELECT DISTINCT * FROM {table_name}',
                f'DROP TABLE {table_name}', f'RENAME TABLE temp TO {table_name}']
        
        self.database_creation()
        


    def database_creation(self):
        cnx = mysql.connector.connect(user=[USERNAME], password=[PASSWORD])
        cursor = cnx.cursor()
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.db_name))
            print('database created!')
        except:
            print('database not created!')
        try:
            cnx.database = self.db_name
            cursor.execute(self._table_query)
            print("table bama created!")
        except:
            print('no need to create table!')
        
        cnx.commit()
        cursor.close()
        cnx.close()

    def insert_data_to_db(self, car_data):
        cnx = mysql.connector.connect(
            user=[USERNAME], password=[PASSWORD], database=self.db_name)
        cursor = cnx.cursor()
        
        for i in car_data:
            cursor.execute(self._insert_query, i)

        cnx.commit()
        cursor.close()
        cnx.close()

    def remove_duplicate_data(self):
        cnx = mysql.connector.connect(
            user=[USERNAME], password=[PASSWORD], database=self.db_name)
        cursor = cnx.cursor()

        for i in self._temp_query:
            try:
                cursor.execute(i)
            except:
                pass
        
        cnx.commit()
        cursor.close()
        cnx.close()