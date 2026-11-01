
from db import get_db_connection

try:
    connection = get_db_connection()

    if connection.is_connected():
        print("SUCCESS: Connected to City Hospital Database!")

        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")

        print("\nTables in database:")
        for table in cursor.fetchall():
            print("-", table[0])

        cursor.close()
        connection.close()

except Exception as error:
    print("Database connection failed:", error)
