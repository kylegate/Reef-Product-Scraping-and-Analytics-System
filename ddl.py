import sqlite3

conn = sqlite3.connect('Bulk_Reef_Supply_DB')
cursor = conn.cursor()

cursor.execute("""DROP TABLE IF EXISTS Product""")

cursor.execute("""CREATE TABLE Product(
ID INTEGER PRIMARY KEY AUTOINCREMENT,
SKU INTEGER,
Name TEXT,
Brand TEXT,
Category TEXT,
Sale_Price REAL,
Price REAL
)""")

conn.commit()
