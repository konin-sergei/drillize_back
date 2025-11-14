[query_title]
Как получить данные из таблицы в базе данных MySQL с помощью кода Python?

[query_title]
Как получить данные из таблицы в базе данных MySQL с помощью кода Python?

[answer_title]
Ответ №1

[answer_content]
Вы можете получить данные из таблицы в базе данных MySQL с помощью библиотеки Python для работы с базами данных - mysql-connector-python. Вот пример кода, который подключается к базе данных MySQL и выполняет запрос SELECT для выборки данных из таблицы:

```py
import mysql.connector

# Подключение к базе данных
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword",
  database="mydatabase"
)

# Выборка данных из таблицы
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM mytable")
myresult = mycursor.fetchall()

# Вывод результатов
for x in myresult:
  print(x)
```

Здесь вы можете заменить "yourusername", "yourpassword", "mydatabase" и "mytable" соответственно на имя пользователя, пароль, название базы данных и таблицы. Вы также можете изменить запрос SELECT, чтобы выбрать только нужные столбцы или добавить условия WHERE для фильтрации результатов.
