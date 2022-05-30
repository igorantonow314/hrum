import sqlite3 as sl

con = sl.connect('test.db')
with con:
	con.execute("""
		CREATE TABLE FRUITS(
			id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			name TEXT,
			price INTEGER
		);
		""")
sql = "INSERT INTO FRUITS (id, name, price) values (?, ?, ?)"
data = [
    (1, 'Apple', 60),
    (2, 'Banana', 70),
    (3, 'Orange', 50)
]
with con:
	con.executemany(sql, data)

with con:
	data = con.execute("SELECT * FROM FRUITS")
	for row in data:
		print(row)
