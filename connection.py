conn = mariadb.connect(
    host='127.0.0.1',
    port=3300,
    ssl_ca="/path/to/skysql_chain.pem",
    user='rajib',
    password='rajib',
    database='tmate',
)

conn.auto_reconnect = True
