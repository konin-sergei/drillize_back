[query_title]
Выполнение команд DML через программы Python?

[query_title]
Выполнение команд DML через программы Python?

[answer_title]
Ответ №1

[answer_content]
Можно выполнять команды DML (Data Manipulation Language) в программе, используя различные библиотеки, такие как Psycopg2 для баз данных PostgreSQL или sqlite3 для баз данных SQLite. Эти библиотеки обеспечивают соединение с базой данных и методы для выполнения запросов к ней, включая запросы SELECT, INSERT, UPDATE и DELETE. Вот пример использования Psycopg2 для выполнения запроса INSERT в базу данных PostgreSQL:
```py
import psycopg2

conn = psycopg2.connect("dbname=mydatabase user=myuser")
cur = conn.cursor()
cur.execute("INSERT INTO mytable (column1, column2, column3) VALUES (%s, %s, %s)", (value1, value2, value3))
conn.commit()
```
А вот пример использования sqlite3 для выполнения запроса SELECT в базе данных SQLite:
```py
import sqlite3

conn = sqlite3.connect('example.db')
cur = conn.cursor()
cur.execute('SELECT * FROM mytable')
results = cur.fetchall()
```
Обратите внимание, что необходимо заменить mydatabase, myuser, mytable и т.д. на соответствующие значения для вашей базы данных.
