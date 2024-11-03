import psycopg2 as pg

conn = None

# TODO: Override connection info

db_connection_str = "host=localhost user=postgres dbname=Assignment3 password=4473 port=5432"

try:
    conn = conn = pg.connect(db_connection_str)
except Exception as err:
    print("Cannot Create DB Connection", err)
