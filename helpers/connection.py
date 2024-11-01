import psycopg2 as pg

conn = None

# TODO: Override connection info

db_connection_str = "host=### user=### dbname=### password=### port=###"

try:
    conn = conn = pg.connect(db_connection_str)
except Exception as err:
    print("Cannot Create DB Connection", err)
