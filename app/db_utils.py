import psycopg2

try:
    connection = psycopg2.connect(
            user = os.environ['DB_USER'],
            password = os.environ['DB_PASSWORD'],
            host = os.environ['DB_HOST'],
            port = os.environ['DB_PORT'],
#            database = os.environ['DB_DB'],
    )

    cursor = connection.cursor()

    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f"You are connect into the - {record}")
except (Exception, psycopg2.Error) as error:
    print("Error connection to PostgreSQL database", error)
    connection = None

finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is now closed")
